import openai
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from textblob import TextBlob
from medicaments.models import Medicament

# Configuration de l'API OpenAI
openai.api_key = settings.OPENAI_API_KEY

# Liste des mots-clés liés à la santé
HEALTH_KEYWORDS = [
    "médicament", "pharmacie", "ordonnance", "traitement", "symptômes", "infection",
    "vitamines", "consultation", "maladie", "vaccin", "soin", "urgence", "hôpital",
    "prescription", "posologie", "allergie", "effets secondaires", "dosage", "médecin"
]

# ==========================
# 📍 Vues pour l'interface utilisateur
# ==========================

def chatbot_view(request):
    """Affiche la page du Chatbot"""
    return render(request, "chatbot.html")

def customer_view(request):
    """Affiche la page du client"""
    return render(request, 'customer_page.html')

# ==========================
# 🏥 Gestion des médicaments
# ==========================

# views.py
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def get_medicaments(request):
    # Get query parameters
    search_query = request.GET.get('search', '')  # Search term
    page = request.GET.get('page', 1)  # Current page, default to 1
    per_page = request.GET.get('per_page', 10)  # Items per page, default to 10

    # Base queryset
    medicaments = Medicament.objects.all()

    # Apply search filter if provided
    if search_query:
        medicaments = medicaments.filter(
            Q(name__icontains=search_query) | Q(generic_name__icontains=search_query)
        )

    # Paginate the results
    paginator = Paginator(medicaments, per_page)
    try:
        paginated_medicaments = paginator.page(page)
    except PageNotAnInteger:
        paginated_medicaments = paginator.page(1)  # Default to page 1 if invalid
    except EmptyPage:
        paginated_medicaments = paginator.page(paginator.num_pages)  # Last page if out of range

    # Prepare data with full image URLs
    data = [
        {
            'id': med.id,
            'name': med.name,
            'generic_name': med.generic_name,
            'selling_price': str(med.selling_price),  # Convert Decimal to string for JSON
            'is_prescription_required': med.is_prescription_required,
            'image': request.build_absolute_uri(med.image.url) if med.image else None
        }
        for med in paginated_medicaments
    ]

    # Return paginated data with metadata
    response_data = {
        'medicaments': data,
        'total': paginator.count,  # Total number of items
        'pages': paginator.num_pages,  # Total number of pages
        'current_page': paginated_medicaments.number,  # Current page number
        'has_next': paginated_medicaments.has_next(),
        'has_previous': paginated_medicaments.has_previous(),
    }
    return JsonResponse(response_data, safe=False)

# ==========================
# 🤖 Chatbot Médical
# ==========================

