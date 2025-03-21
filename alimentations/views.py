import logging
from datetime import datetime

from django.contrib import auth

from utils.permissions import is_admin

logger = logging.getLogger(__name__)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from alimentations.models import Alimentation
from medicaments.models import Medicament
from stocks.models import Stock

util_form = 'alimentations/medicament_form.html'

from utils.is_ajax_request import is_ajax_request

@user_passes_test(is_admin)
def index(request):
    if is_ajax_request(request):
        alimentations = Alimentation.objects.all().values(
            'id', 'quantity', 'purchase_price', 'expiry_date'
        )

        alimentation_list = [{
            **alimentation,
            'name': str(Alimentation.objects.get(id=alimentation['id']))
        } for alimentation in alimentations]

        return JsonResponse(alimentation_list, safe=False)

    return render(request, 'alimentations/index.html', context={
        'title': 'Alimentations List',
        'message': 'Alimentations List',
    })

@csrf_protect
@user_passes_test(is_admin)
def create_alimentation(request):
    global expiry_date, medicament
    if is_ajax_request(request) and request.method == 'POST':
        errors = {}

        try:
            medicament_id = request.POST.get('medicament_id')
            batch_number = request.POST.get('batch_number')
            quantity = request.POST.get('quantity')
            purchase_price = request.POST.get('purchase_price')
            expiry_date_str = request.POST.get('expiry_date')
            selling_price = request.POST.get('selling_price')

            if not medicament_id:
                errors['medicament_id'] = 'Select a medicament'
            else:
                medicament = get_object_or_404(Medicament, pk=medicament_id)

            if not batch_number.isdigit():
                errors['batch_number'] = 'Batch number must be an integer.'
            else:
                batch_number = int(batch_number)

            if not quantity.isdigit() or int(quantity) <= 0:
                errors['quantity'] = 'Quantity must be a positive integer.'
            else:
                quantity = int(quantity)

            try:
                purchase_price = float(purchase_price)
                if purchase_price <= 0:
                    errors['purchase_price'] = 'Purchase price must be greater than zero.'
            except ValueError:
                errors['purchase_price'] = 'Purchase price must be a valid number.'

            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                if expiry_date <= datetime.today().date():  # Compare with .date()
                    errors['expiry_date'] = 'Expiry date must be greater than today\'s date.'
            except ValueError:
                errors['expiry_date'] = 'Invalid expiry date format. Use YYYY-MM-DD.'

            try:
                selling_price = float(selling_price)
                if selling_price <= 0:
                    errors['selling_price'] = 'Selling price must be greater than zero.'
            except ValueError:
                errors['selling_price'] = 'Selling price must be a valid number.'

            if errors:
                return JsonResponse({'errors': errors}, status=400)

            with transaction.atomic():
                alimentation = Alimentation(
                    batch_number=batch_number,
                    quantity=quantity,
                    purchase_price=purchase_price,
                    expiry_date=expiry_date,
                    medicament=medicament,
                )
                alimentation.full_clean()
                alimentation.save()
                medicament.update_prices(purchase_price=purchase_price, selling_price=selling_price)
                stock, created = Stock.objects.get_or_create(medicament_id=medicament_id)
                stock.update_quantity_in(quantity=quantity, previous_quantity=0)

                return JsonResponse({'message': 'Alimentation added successfully.'})

        except Exception as e:
            return JsonResponse({'errors': {'general': str(e)}}, status=400)

    else:
        medicaments = Medicament.objects.all()
        return render(request, 'alimentations/alimentation_form.html', {'medicaments': medicaments})

@user_passes_test(is_admin)
def edit_alimentation(request, alimentation_id):
    alimentation = get_object_or_404(Alimentation, id=alimentation_id)

    if is_ajax_request(request) and request.method == 'POST':
        errors = {}

        try:
            medicament_id = request.POST.get('medicament_id')
            batch_number = request.POST.get('batch_number')
            quantity = request.POST.get('quantity')
            purchase_price = request.POST.get('purchase_price')
            expiry_date_str = request.POST.get('expiry_date')
            selling_price = request.POST.get('selling_price')
            previous_quantity = alimentation.quantity

            if not medicament_id:
                errors['medicament_id'] = 'Select a medicament'
            else:
                medicament = get_object_or_404(Medicament, pk=medicament_id)

            if not batch_number.isdigit():
                errors['batch_number'] = 'Batch number must be an integer.'
            else:
                batch_number = int(batch_number)

            if not quantity.isdigit() or int(quantity) <= 0:
                errors['quantity'] = 'Quantity must be a positive integer.'
            else:
                quantity = int(quantity)

            try:
                purchase_price = float(purchase_price)
                if purchase_price <= 0:
                    errors['purchase_price'] = 'Purchase price must be greater than zero.'
            except ValueError:
                errors['purchase_price'] = 'Purchase price must be a valid number.'

            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()  # Convert to date object
                if expiry_date <= datetime.today().date():
                    errors['expiry_date'] = 'Expiry date must be greater than today\'s date.'
            except ValueError:
                errors['expiry_date'] = 'Invalid expiry date format. Use YYYY-MM-DD.'

            try:
                selling_price = float(selling_price)
                if selling_price <= 0:
                    errors['selling_price'] = 'Selling price must be greater than zero.'
            except ValueError:
                errors['selling_price'] = 'Selling price must be a valid number.'

            if errors:
                return JsonResponse({'errors': errors}, status=400)

            # If no errors, proceed with the database update
            with transaction.atomic():
                alimentation.batch_number = batch_number
                alimentation.quantity = quantity
                alimentation.purchase_price = purchase_price
                alimentation.expiry_date = expiry_date
                alimentation.medicament = medicament
                alimentation.full_clean()

                alimentation.save()
                alimentation.full_clean()
                alimentation.save()
                medicament.update_prices(purchase_price=purchase_price, selling_price=selling_price)
                stock, created = Stock.objects.get_or_create(medicament_id=medicament_id)
                stock.update_quantity_in(quantity=quantity, previous_quantity = previous_quantity)
                return JsonResponse({'message': 'Alimentation updated successfully.'})

        except Exception as e:
            logger.exception('An error occurred: %s', e)
            return JsonResponse({'errors': {'general': str(e)}}, status=400)

    else:
        medicaments = Medicament.objects.all()
        return render(request, 'alimentations/alimentation_form.html', {
            'medicaments': medicaments,
            'alimentation': alimentation,
        })


@user_passes_test(is_admin)
@csrf_protect
def delete_alimentation(request, alimentation_id):
    if is_ajax_request(request) and request.method == 'DELETE':
        with transaction.atomic():
            try:
                alimentation = get_object_or_404(Alimentation, id=alimentation_id)
                stock = get_object_or_404(Stock, medicament_id=alimentation.medicament.id)
                stock.quantity_in -= alimentation.quantity
                stock.quantity_current = stock.quantity_in - stock.quantity_out
                stock.save()

                alimentation.delete()

                return JsonResponse({'status': 'success', 'message': 'Alimentation deleted, stock updated.'})

            except Alimentation.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Alimentation not found.'}, status=404)

            except Stock.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Stock entry not found.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
