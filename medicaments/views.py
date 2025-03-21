from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from utils.permissions import is_admin
from .models import Medicament, Category
from utils.enums.enums import PrescriptionRequiredEnum
from utils.is_ajax_request import is_ajax_request

util_form = 'medicaments/medicament_form.html'

@user_passes_test(is_admin)
def index(request):
    if is_ajax_request(request):
        medicaments = Medicament.objects.all().values(
            'id', 'name', 'generic_name', 'category', 'dosage', 'unit_type',
            'manufacturer', 'storage_conditions', 'is_prescription_required',
            'image', 'purchase_price', 'selling_price', 'created_at', 'updated_at'
        )
        medicament_list = list(medicaments)
        return JsonResponse(medicament_list, safe=False)
    return render(request, 'medicaments/index.html', context={
        'title': 'Medicament List',
        'message': 'Medicament List',
    })


@login_required
def create_medicament(request):
    if is_ajax_request(request) and request.method == 'POST':
        errors = {}
        try:
            category_name = request.POST.get('category', '').strip()
            if not category_name:
                errors['category'] = 'Category name cannot be empty.'
            else:
                category, created = Category.objects.get_or_create(name=category_name)

            # Validate each field individually
            name = request.POST.get('name')
            if not name:
                errors['name'] = 'Name cannot be empty.'

            generic_name = request.POST.get('generic_name')
            if not generic_name:
                errors['generic_name'] = 'Generic name cannot be empty.'

            dosage = request.POST.get('dosage')
            if not dosage:
                errors['dosage'] = 'Dosage cannot be empty.'

            unit_type = request.POST.get('unit_type')
            if not unit_type:
                errors['unit_type'] = 'Unit type cannot be empty.'

            manufacturer = request.POST.get('manufacturer')
            if not manufacturer:
                errors['manufacturer'] = 'Manufacturer cannot be empty.'

            storage_conditions = request.POST.get('storage_conditions')
            if not storage_conditions:
                errors['storage_conditions'] = 'Storage conditions cannot be empty.'

            is_prescription_required = request.POST.get('is_prescription_required')
            if not is_prescription_required:
                errors['is_prescription_required'] = 'Prescription requirement must be specified.'

            image = request.FILES.get('image')

            if errors:
                return JsonResponse({'errors': errors}, status=400)

            # Create and save the Medicament instance
            medicament = Medicament(
                name=name,
                generic_name=generic_name,
                category=category,
                dosage=dosage,
                unit_type=unit_type,
                manufacturer=manufacturer,
                storage_conditions=storage_conditions,
                is_prescription_required=is_prescription_required,
                image=image,
                # purchase_price=purchase_price,
                # selling_price=selling_price
            )
            medicament.full_clean()  # Validate the model instance
            medicament.save()

            return JsonResponse({'message': 'Medicament added successfully.'})

        except ValidationError as e:
            errors.update(e.message_dict)
            return JsonResponse({'errors': errors}, status=400)
        except Exception as e:
            errors['non_field_errors'] = str(e)
            return JsonResponse({'errors': errors}, status=400)

    else:
        categories = Category.objects.all()
        return render(request, util_form, {
            'categories': categories,
            'prescription_required_enum': PrescriptionRequiredEnum.choices()
        })


@login_required
def edit_medicament(request, medicament_id):
    medicament = get_object_or_404(Medicament, id=medicament_id)

    if request.method == 'POST':
        errors = {}
        try:
            category_name = request.POST.get('category', '').strip()
            if not category_name:
                errors['category'] = 'Category name cannot be empty.'
            else:
                category, created = Category.objects.get_or_create(name=category_name)

            # Validate each field individually
            name = request.POST.get('name')
            if not name:
                errors['name'] = 'Name cannot be empty.'

            generic_name = request.POST.get('generic_name')
            if not generic_name:
                errors['generic_name'] = 'Generic name cannot be empty.'

            dosage = request.POST.get('dosage')
            if not dosage:
                errors['dosage'] = 'Dosage cannot be empty.'

            unit_type = request.POST.get('unit_type')
            if not unit_type:
                errors['unit_type'] = 'Unit type cannot be empty.'

            manufacturer = request.POST.get('manufacturer')
            if not manufacturer:
                errors['manufacturer'] = 'Manufacturer cannot be empty.'

            storage_conditions = request.POST.get('storage_conditions')
            if not storage_conditions:
                errors['storage_conditions'] = 'Storage conditions cannot be empty.'

            is_prescription_required = request.POST.get('is_prescription_required')
            if not is_prescription_required:
                errors['is_prescription_required'] = 'Prescription requirement must be specified.'

            # purchase_price = request.POST.get('purchase_price')
            # if not purchase_price:
            #     errors['purchase_price'] = 'Purchase price cannot be empty.'
            # else:
            #     try:
            #         purchase_price = float(purchase_price)
            #     except ValueError:
            #         errors['purchase_price'] = 'Purchase price must be a valid number.'
            #
            # selling_price = request.POST.get('selling_price')
            # if not selling_price:
            #     errors['selling_price'] = 'Selling price cannot be empty.'
            # else:
            #     try:
            #         selling_price = float(selling_price)
            #     except ValueError:
            #         errors['selling_price'] = 'Selling price must be a valid number.'

            image = request.FILES.get('image')

            if errors:
                return JsonResponse({'errors': errors}, status=400)

            medicament.name = name
            medicament.generic_name = generic_name
            medicament.category = category
            medicament.dosage = dosage
            medicament.unit_type = unit_type
            medicament.manufacturer = manufacturer
            medicament.storage_conditions = storage_conditions
            medicament.is_prescription_required = is_prescription_required
            if image:
                medicament.image = image
            # medicament.purchase_price = purchase_price
            # medicament.selling_price = selling_price

            medicament.full_clean()  # Validate the model instance
            medicament.save()

            return JsonResponse({'message': 'Medicament updated successfully.'})

        except ValidationError as e:
            errors.update(e.message_dict)
            return JsonResponse({'errors': errors}, status=400)
        except Exception as e:
            errors['non_field_errors'] = str(e)
            return JsonResponse({'errors': errors}, status=400)

    else:
        categories = Category.objects.all()
        return render(request, util_form, {
            'categories': categories,
            'medicament': medicament,
            'prescription_required_enum': PrescriptionRequiredEnum.choices(),
        })



@login_required
@csrf_protect
def delete_medicament(request, medicament_id):
    if request.method == 'POST':
        try:
            medicament = Medicament.objects.get(id=medicament_id)
            medicament.delete()
            return JsonResponse({'status': 'success', 'message': 'Medicament deleted successfully.'})
        except Medicament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Medicament not found.'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@login_required
def view_medicament(request, medicament_id):
    medicament = get_object_or_404(Medicament, id=medicament_id)
    return render(request, 'medicaments/view.html', {'medicament': medicament})


def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Vous devez être connecté pour ajouter un produit au panier.'}, status=401)

    medicament_id = request.POST.get('medicament_id')
    medicament = Medicament.objects.filter(id=medicament_id).first()

    if not medicament:
        return JsonResponse({'error': 'Médicament introuvable'}, status=404)

    # Simulation d'ajout au panier (vous pouvez stocker cela en session ou en base)
    return JsonResponse({'message': f'{medicament.name} ajouté au panier !'}, status=200)