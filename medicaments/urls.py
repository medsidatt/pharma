from django.urls import path
from . import views  # Import views from the same directory
from .views import edit_medicament, add_to_cart

app_name = 'medicaments'  # Namespace for reverse()

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_medicament, name='create'),
    path('edit/<int:medicament_id>/', edit_medicament, name='edit'),
    path('delete/<int:medicament_id>/', views.delete_medicament, name='delete_medicament'),
    path('view/<int:medicament_id>/', views.view_medicament, name='view_medicament'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('create-sample-medicaments/', views.create_sample_medicaments, name='create_sample_medicaments'),

]
