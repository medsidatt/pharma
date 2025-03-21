from django.db import models
from django.conf import settings  # Importer settings pour AUTH_USER_MODEL
from medicaments.models import Medicament

class OrderStatus(models.TextChoices):
    PENDING = "pending", "En attente"
    VALIDATED = "validated", "Validée"
    REJECTED = "rejected", "Refusée"

class ReceptionStatus(models.TextChoices):
    NOT_RECEIVED = "not_received", "Non reçue"
    RECEIVED = "received", "Reçue"

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Correction ici
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    reception_status = models.CharField(
        max_length=15, choices=ReceptionStatus.choices, default=ReceptionStatus.NOT_RECEIVED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def validate_order(self):
        self.status = OrderStatus.VALIDATED
        self.save()

    def reject_order(self):
        self.status = OrderStatus.REJECTED
        self.save()

    def mark_as_received(self):
        if self.status == OrderStatus.VALIDATED:
            self.reception_status = ReceptionStatus.RECEIVED
            self.save()


from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    def mark_as_read(self):
        self.is_read = True
        self.save()
