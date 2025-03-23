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

# @login_required
# def chatbot_response(request):
#     """Répond uniquement aux questions liées à la santé, sinon renvoie un message de refus."""
#     if request.method != "POST":
#         return JsonResponse({"error": "Méthode non autorisée"}, status=405)
#
#     user_message = request.POST.get("message", "").strip()
#
#     if not user_message:
#         return JsonResponse({"error": "Veuillez entrer une question."}, status=400)
#
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "Tu es un assistant médical. Réponds uniquement aux questions sur la santé et les médicaments. "
#                         "Si une question ne concerne pas la santé, réponds : "
#                         "'Je ne peux répondre qu'aux questions liées à la santé et aux médicaments.'"
#                     )
#                 },
#                 {"role": "user", "content": user_message}
#             ]
#         )
#
#         bot_message = response["choices"][0]["message"]["content"]
#
#         # Vérification finale pour éviter un contournement
#         if "je ne peux répondre qu'aux questions liées à la santé" in bot_message.lower():
#             return JsonResponse({
#                 "message": "❌ Désolé, je réponds uniquement aux questions liées à la santé et aux médicaments."
#             }, status=200)
#
#         return JsonResponse({"message": bot_message})
#
#     except Exception as e:
#         return JsonResponse({
#             "error": "Une erreur est survenue. Merci de réessayer.",
#             "details": str(e)  # Utile pour debug (peut être retiré en prod)
#         }, status=500)

# views.py
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Hugging Face API setup
API_TOKEN = "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"  # Your API token
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}
MODEL_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

@login_required  # Restrict to logged-in users
def chatbot_response(request):
    if request.method == "POST":
        question = request.POST.get("message", "").strip()  # Match template's 'message' key
        if not question:
            return JsonResponse({"message": "Please enter a question."}, status=400)

        # Send question to Hugging Face API
        payload = {
            "inputs": question,
            "parameters": {
                "max_length": 100,
                "temperature": 0.7,
                "top_k": 50,
                "do_sample": True
            }
        }
        try:
            response = requests.post(MODEL_URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                answer = result[0].get("generated_text", "Sorry, I couldn’t generate a response.")
                return JsonResponse({"message": answer})  # Match template's expectation
            return JsonResponse({"message": "No response from the model."}, status=500)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"message": f"API error: {str(e)}"}, status=500)

    return JsonResponse({"message": "Invalid request method."}, status=400)