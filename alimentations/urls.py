from django.urls import path

from alimentations import views
from alimentations.views import edit_alimentation

app_name = 'alimentations'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_alimentation, name='create'),
    # path('api/alimentations/', alimentation_list_json, name='alimentation_list_json'),
    path('edit/<int:alimentation_id>/', edit_alimentation, name='edit'),
    path('delete/<int:alimentation_id>/', views.delete_alimentation, name='delete_alimentation'),

]