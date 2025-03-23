from django.urls import path

from manager import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('get_pharma_stats/', views.get_pharma_stats, name='get_pharma_stats'),
]