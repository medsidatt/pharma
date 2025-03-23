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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Medicament
from utils.enums.enums import PrescriptionRequiredEnum
import random

@csrf_exempt  # For simplicity; remove in production or add CSRF protection
def create_sample_medicaments(request):
    """Endpoint to create 20 sample medicaments for testing"""
    if request.method == "POST":
        try:
            # Ensure some categories exist
            categories = [
                "Analgesics", "Antibiotics", "Antivirals", "Cardiovascular", "Vitamins"
            ]
            for cat_name in categories:
                Category.objects.get_or_create(name=cat_name)

            # Sample data for medicaments
            sample_medicaments = [
                {"name": "Paracetamol", "generic_name": "Acetaminophen", "category": "Analgesics", "dosage": "500mg", "unit_type": "Tablet", "manufacturer": "PharmaCo", "storage_conditions": "Room Temp", "is_prescription_required": "NO"},
                {"name": "Ibuprofen", "generic_name": "Ibuprofen", "category": "Analgesics", "dosage": "200mg", "unit_type": "Tablet", "manufacturer": "MediCorp", "storage_conditions": "Cool Dry Place", "is_prescription_required": "NO"},
                {"name": "Amoxicillin", "generic_name": "Amoxicillin", "category": "Antibiotics", "dosage": "250mg", "unit_type": "Capsule", "manufacturer": "BioPharma", "storage_conditions": "Refrigerate", "is_prescription_required": "YES"},
                {"name": "Ciprofloxacin", "generic_name": "Ciprofloxacin", "category": "Antibiotics", "dosage": "500mg", "unit_type": "Tablet", "manufacturer": "Genix", "storage_conditions": "Room Temp", "is_prescription_required": "YES"},
                {"name": "Oseltamivir", "generic_name": "Oseltamivir", "category": "Antivirals", "dosage": "75mg", "unit_type": "Capsule", "manufacturer": "ViroMed", "storage_conditions": "Cool Dry Place", "is_prescription_required": "YES"},
                {"name": "Acyclovir", "generic_name": "Acyclovir", "category": "Antivirals", "dosage": "400mg", "unit_type": "Tablet", "manufacturer": "PharmaCo", "storage_conditions": "Room Temp", "is_prescription_required": "YES"},
                {"name": "Atenolol", "generic_name": "Atenolol", "category": "Cardiovascular", "dosage": "50mg", "unit_type": "Tablet", "manufacturer": "CardioLabs", "storage_conditions": "Room Temp", "is_prescription_required": "YES"},
                {"name": "Lisinopril", "generic_name": "Lisinopril", "category": "Cardiovascular", "dosage": "10mg", "unit_type": "Tablet", "manufacturer": "MediCorp", "storage_conditions": "Cool Dry Place", "is_prescription_required": "YES"},
                {"name": "Vitamin C", "generic_name": "Ascorbic Acid", "category": "Vitamins", "dosage": "1000mg", "unit_type": "Tablet", "manufacturer": "NutriHealth", "storage_conditions": "Room Temp", "is_prescription_required": "NO"},
                {"name": "Vitamin D3", "generic_name": "Cholecalciferol", "category": "Vitamins", "dosage": "2000IU", "unit_type": "Capsule", "manufacturer": "VitaLabs", "storage_conditions": "Cool Dry Place", "is_prescription_required": "NO"},
                {"name": "Aspirin", "generic_name": "Acetylsalicylic Acid", "category": "Analgesics", "dosage": "81mg", "unit_type": "Tablet", "manufacturer": "PharmaCo", "storage_conditions": "Room Temp", "is_prescription_required": "NO"},
                {"name": "Azithromycin", "generic_name": "Azithromycin", "category": "Antibiotics", "dosage": "500mg", "unit_type": "Tablet", "manufacturer": "BioPharma", "storage_conditions": "Refrigerate", "is_prescription_required": "YES"},
                {"name": "Metformin", "generic_name": "Metformin", "category": "Cardiovascular", "dosage": "500mg", "unit_type": "Tablet", "manufacturer": "Genix", "storage_conditions": "Room Temp", "is_prescription_required": "YES"},
                {"name": "Omeprazole", "generic_name": "Omeprazole", "category": "Gastrointestinal", "dosage": "20mg", "unit_type": "Capsule", "manufacturer": "MediCorp", "storage_conditions": "Cool Dry Place", "is_prescription_required": "NO"},
                {"name": "Loratadine", "generic_name": "Loratadine", "category": "Antihistamines", "dosage": "10mg", "unit_type": "Tablet", "manufacturer": "PharmaCo", "storage_conditions": "Room Temp", "is_prescription_required": "NO"},
                {"name": "Simvastatin", "generic_name": "Simvastatin", "category": "Cardiovascular", "dosage": "20mg", "unit_type": "Tablet", "manufacturer": "CardioLabs", "storage_conditions": "Room Temp", "is_prescription_required": "YES"},
                {"name": "Levothyroxine", "generic_name": "Levothyroxine", "category": "Hormones", "dosage": "50mcg", "unit_type": "Tablet", "manufacturer": "BioPharma", "storage_conditions": "Cool Dry Place", "is_prescription_required": "YES"},
                {"name": "Prednisone", "generic_name": "Prednisone", "category": "Corticosteroids", "dosage": "10mg", "unit_type": "Tablet", "manufacturer": "Genix", "storage_conditions": "Room Temp", "is_prescription_required": "YES"},
                {"name": "Folic Acid", "generic_name": "Folic Acid", "category": "Vitamins", "dosage": "400mcg", "unit_type": "Tablet", "manufacturer": "NutriHealth", "storage_conditions": "Room Temp", "is_prescription_required": "NO"},
                {"name": "Cetirizine", "generic_name": "Cetirizine", "category": "Antihistamines", "dosage": "10mg", "unit_type": "Tablet", "manufacturer": "VitaLabs", "storage_conditions": "Cool Dry Place", "is_prescription_required": "NO"},
            ]

            # Create medicaments
            for med in sample_medicaments:
                category = Category.objects.get(name=med["category"])
                Medicament.objects.create(
                    name=med["name"],
                    generic_name=med["generic_name"],
                    category=category,
                    dosage=med["dosage"],
                    unit_type=med["unit_type"],
                    manufacturer=med["manufacturer"],
                    storage_conditions=med["storage_conditions"],
                    is_prescription_required=med["is_prescription_required"],
                    purchase_price=random.uniform(1.0, 50.0),  # Random price for testing
                    selling_price=random.uniform(2.0, 60.0),   # Random price for testing
                )

            return JsonResponse({'message': '20 sample medicaments created successfully.'})
        except Exception as e:
            return JsonResponse({'errors': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Use POST to create sample medicaments.'}, status=405)