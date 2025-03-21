# stocks/urls.py
from django.urls import path

from stocks.views import stock_list, stock_list_json

app_name = 'stocks'
urlpatterns = [
    path('', stock_list, name='index'),
    # path('api/stocks/', stock_list_json, name='api-stocks'),
]