from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.db import models

from medicaments.models import Medicament


class Alimentation(models.Model):
    batch_number = models.IntegerField()
    expiry_date = models.DateTimeField()
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    medicament = models.ForeignKey(
        Medicament,
        on_delete=models.CASCADE,
        related_name='alimentations',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.batch_number} - {self.medicament.name}"