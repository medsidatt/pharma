from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import get_medicaments #, chatbot_response, chatbot_view

urlpatterns = [
    # path('', views.customer_view, name='customer-view'),
    path('get-medicaments/', get_medicaments, name='get_medicaments'),
    # path("chatbot/", chatbot_view, name="chatbot"),
    # path("chatbot_response/", chatbot_response, name="chatbot_response"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)