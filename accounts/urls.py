from django.contrib.auth.decorators import user_passes_test
from django.urls import path
from django.contrib.auth import views as auth_views

from utils.app import is_not_authenticated
from . import views
from .form import CustomLoginView
from .views import logout_view, register_view, login_view

urlpatterns = [
    path('register/', user_passes_test(is_not_authenticated, login_url='/')(register_view), name='register'),
    path('login/',login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', views.home_view, name='home'),
]