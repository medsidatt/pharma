from django.urls import path
from .views import (
    place_order, validate_order, reject_order, mark_order_received,
    view_orders, get_notifications, clear_notifications, fetch_orders, admin_orders, orders_view, notifications_page
)

urlpatterns = [
    path("place-order/", place_order, name="place_order"),
    path("validate-order/<int:order_id>/", validate_order, name="validate_order"),
    path("reject-order/<int:order_id>/", reject_order, name="reject_order"),
    path("mark-received/<int:order_id>/", mark_order_received, name="mark_order_received"),
    path("view-orders/", view_orders, name="view_orders"),
    # path("view-all-orders/", view_all_orders, name="view_all_orders"),  # Nouvelle URL
    path("get-notifications/", get_notifications, name="get_notifications"),
    path("clear-notifications/", clear_notifications, name="clear_notifications"),
    # path("orders/", admin_orders, name="admin_orders"),
    path("orders/", orders_view, name="orders"),
    path("fetch_orders", fetch_orders, name="fetch_orders"),
    path("notifications_page", notifications_page, name="notifications_page"),
]
