# Create your views here.
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from medicaments.models import Medicament
from orders.models import Order
from stocks.models import Stock

def dashboard(request):
    return render(request, "dashboard.html")


User = get_user_model()

def get_pharma_stats(request):
    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())

    # Statistiques de base
    data = {
        'total_utilisateurs': User.objects.count(),
        'total_commandes': Order.objects.count(),
        'commandes_en_attente': Order.objects.filter(status='pending').count(),
        'commandes_validees': Order.objects.filter(status='validated').count(),
        'commandes_livrees': Order.objects.filter(reception_status='received').count(),
        'total_medicaments': Medicament.objects.count(),
        'ruptures_stock': Stock.objects.filter(quantity_current__lte=5).count(),
        'ventes_totales': Order.objects.filter(status='validated').aggregate(total=Sum('total_price'))['total'] or 0,
    }

    # Ventes par jour de la semaine (graphique)
    sales_by_day = []
    day_labels = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    for i in range(7):
        date_i = start_of_week + timedelta(days=i)
        ventes = Order.objects.filter(status='validated', created_at__date=date_i.date()).aggregate(total=Sum('total_price'))['total'] or 0
        sales_by_day.append(ventes)

    data['series_ventes'] = {
        'labels': day_labels,
        'values': sales_by_day
    }

    # Statuts des commandes (graphique radial)
    data['statut_commandes'] = {
        'pending': data['commandes_en_attente'],
        'validated': data['commandes_validees'],
        'delivered': data['commandes_livrees'],
        'cancelled': Order.objects.filter(status='cancelled').count()
    }

    # Médicaments les plus vendus (par quantité commandée)
    top_meds = (
        Order.objects.filter(status='validated')
        .values('medicament')
        .annotate(total_ventes=Sum('quantity'))
        .order_by('-total_ventes')[:4]
    )

    popular_meds = []
    for item in top_meds:
        try:
            med = Medicament.objects.get(pk=item['medicament'])
            stock = Stock.objects.filter(medicament=med).first()
            popular_meds.append({
                'nom': med.name,
                'ventes': item['total_ventes'],
                'stock': stock.quantity_current if stock else 0
            })
        except Medicament.DoesNotExist:
            continue

    data['medicaments_populaires'] = popular_meds

    # Réponse JSON pour AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(data)

    # Si non AJAX : rendre un template HTML
    return render(request, 'dashboard/pharma_dashboard.html', data)
