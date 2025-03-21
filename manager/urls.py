from django.urls import path

from manager import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]