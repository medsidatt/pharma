import logging
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from twilio.rest import Client

from medicaments.models import Medicament
from stocks.models import Stock
from orders.models import Order, OrderStatus, ReceptionStatus, Notification
from utils.permissions import is_not_customer
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Notification

# ========================== LOGGER ==========================
logger = logging.getLogger(__name__)


# ============================================================
# 🛒 ORDER MANAGEMENT VIEWS (FOR USERS)
# ============================================================

@login_required
def place_order(request):
    """Créer une commande et notifier l'admin"""
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    medicament_id = request.POST.get("medicament_id")
    quantity = int(request.POST.get("quantity", 1))

    medicament = Medicament.objects.filter(id=medicament_id).first()
    if not medicament:
        return JsonResponse({"error": "Médicament introuvable"}, status=404)

    total_price = medicament.selling_price * quantity
    order = Order.objects.create(
        user=request.user,
        medicament=medicament,
        quantity=quantity,
        total_price=total_price
    )

    # 🔔 Notify all admin users
    User = get_user_model()
    admin_users = User.objects.filter(is_superuser=True)
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            message=f"Nouvelle commande #{order.id} de {request.user.username} - {order.quantity}x {order.medicament.name}."
        )

    return JsonResponse({"message": "Commande passée avec succès!", "order_id": order.id}, status=201)

@login_required
def view_orders(request):
    """Afficher les commandes de l'utilisateur"""
    orders = Order.objects.filter(user=request.user).values(
        "id", "medicament__name", "quantity", "total_price", "status", "reception_status", "created_at"
    )
    return JsonResponse(list(orders), safe=False)


@login_required
def mark_order_received(request, order_id):
    """Marquer une commande comme reçue"""
    order = Order.objects.filter(id=order_id, status=OrderStatus.VALIDATED, reception_status=ReceptionStatus.NOT_RECEIVED).first()

    if not order:
        return JsonResponse({"error": "Commande introuvable ou non validée"}, status=404)

    order.mark_as_received()
    return JsonResponse({"message": "Commande marquée comme reçue!"})


# ============================================================
# 🎯 ORDER MANAGEMENT (FOR ADMIN)
# ============================================================

def is_admin(user):
    """Vérifie si l'utilisateur est un administrateur"""
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_admin)
def fetch_orders(request):
    """Récupérer les commandes paginées pour l'admin"""
    status = request.GET.get("status", "all")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))

    try:
        orders_query = Order.objects.select_related("user", "medicament").order_by("-created_at")
        if date := request.GET.get("date"):
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d").date()
                orders_query = orders_query.filter(created_at__date=date_obj)
            except ValueError:
                return JsonResponse({"error": "Date invalide."}, status=400)

        if status != "all":
            orders_query = orders_query.filter(status=status)

        total_orders = orders_query.count()
        total_pages = (total_orders // limit) + (1 if total_orders % limit > 0 else 0)

        orders = orders_query[(page - 1) * limit: page * limit].values(
            "id", "user__username", "medicament__name", "quantity", "total_price",
            "status", "reception_status", "created_at"
        )

        orders_list = [
            {
                "id": order["id"],
                "user": order["user__username"],
                "medicament": order["medicament__name"],
                "quantity": order["quantity"],
                "total_price": order["total_price"],
                "status": {
                    "value": order["status"],
                    "label": dict(OrderStatus.choices).get(order["status"], order["status"]),
                },
                "reception_status": {
                    "value": order["reception_status"],
                    "label": dict(ReceptionStatus.choices).get(order["reception_status"], order["reception_status"]),
                },
                "created_at": order["created_at"].strftime("%d/%m/%Y %H:%M"),
            }
            for order in orders
        ]

        return JsonResponse({"orders": orders_list, "total_orders": total_orders, "total_pages": total_pages})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def validate_order(request, order_id):
    print("##333333333333333333333333333333, order_id:", order_id)
    """Valider une commande après vérification du stock"""
    order = Order.objects.select_related("medicament").filter(id=order_id, status=OrderStatus.PENDING).first()

    if not order:
        return JsonResponse({"error": "Commande introuvable ou déjà traitée"}, status=404)

    stock = Stock.objects.filter(medicament=order.medicament).first()

    if not stock or stock.quantity_current < order.quantity:
        return JsonResponse({"error": "Stock insuffisant pour valider la commande."}, status=400)

    stock.update_quantity_out(order.quantity)

    order.status = OrderStatus.VALIDATED
    order.save()

    send_whatsapp_notification(order)

    return JsonResponse({"message": "Commande validée avec succès et notification envoyée!"})


@login_required
@user_passes_test(is_admin)
def reject_order(request, order_id):
    """Refuser une commande"""
    order = Order.objects.filter(id=order_id, status=OrderStatus.PENDING).first()
    if not order:
        return JsonResponse({"error": "Commande introuvable ou déjà traitée"}, status=404)

    order.reject_order()
    return JsonResponse({"message": "Commande refusée!"})


# ============================================================
# 🔔 NOTIFICATIONS (FOR ADMIN)
# ============================================================

@login_required
@user_passes_test(is_admin)


def get_notifications(request):
    status = request.GET.get('status', 'all')
    date_filter = request.GET.get('date')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))

    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")

    if status == 'read':
        notifications = notifications.filter(is_read=True)
    elif status == 'unread':
        notifications = notifications.filter(is_read=False)

    if date_filter:
        notifications = notifications.filter(created_at__date=date_filter)

    paginator = Paginator(notifications, limit)
    page_obj = paginator.get_page(page)

    notifications_list = [
        {
            "id": notif.id,
            "message": notif.message,
            "is_read": notif.is_read,
            "created_at": notif.created_at.strftime("%d/%m/%Y %H:%M"),
        }
        for notif in page_obj
    ]

    return JsonResponse({
        "notifications": notifications_list,
        "total_pages": paginator.num_pages,
        "current_page": page,
        "has_previous": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
    })


@login_required
@user_passes_test(is_admin)
def clear_notifications(request):
    """Marquer toutes les notifications comme lues"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"message": "Notifications marquées comme lues.", "status": "success"})



# ============================================================
# 📲 WHATSAPP NOTIFICATIONS VIA TWILIO
# ============================================================

def send_whatsapp_notification(order):
    """Envoie un message WhatsApp au client après validation de la commande"""

    user_phone = getattr(order.user, "phone_number", None)
    if not user_phone:
        logger.error(f"WhatsApp notification failed: No phone number for user {order.user.username}.")
        return


    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    message_body = f"""
    ✅ [MediQuick] Commande validée ✅
    Bonjour {order.user.username}, 
    Votre commande #{order.id} pour {order.quantity}x {order.medicament.name} a été validée.
    Total: {order.total_price} MRU.

    Merci pour votre confiance! 🏥💊
    """

    try:
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=f"whatsapp:{user_phone}"
        )
        logger.info(f"WhatsApp Message Sent: {message.sid} to {user_phone}")

    except Exception as e:
        logger.error(f"Erreur en envoyant WhatsApp: {str(e)}")


# ============================================================
# 🎯 ADMIN PANEL
# ============================================================

@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    """Affiche la page de gestion des commandes pour l'admin"""
    return render(request, "admin_orders.html", {"title": "Gestion des Commandes"})


@login_required
def orders_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, "admin_orders.html", {"title": "Gestion des Commandes"})
        elif request.user.is_customer:
            return render(request, 'customer_orders.html')
    else:
        return


@user_passes_test(is_admin)
def notifications_page(request):
    return render(request, 'notification.html')
