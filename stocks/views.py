from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from stocks.models import Stock
from utils.is_ajax_request import is_ajax_request


@login_required
def stock_list(request):
    if is_ajax_request(request):
        stocks = Stock.objects.all().values(
            'id', 'quantity_in', 'quantity_out', 'quantity_current'
        )
        stocks = [{
            **stock,
            'name': str(Stock.objects.get(id=stock['id']))
        } for stock in stocks]
        return JsonResponse(stocks, safe=False)
    return render(request, 'stocks/stock_page.html')


@login_required
def stock_list_json(request):
    stocks = Stock.objects.all().values(
        'id', 'quantity_in', 'quantity_out', 'quantity_current'
    )

    stock_list = [{
        **stock,
        'name': str(Stock.objects.get(id=stock['id']))
    } for stock in stocks]

    return JsonResponse(stock_list, safe=False)
