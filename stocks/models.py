from django.db import models

from medicaments.models import Medicament


class Stock(models.Model):
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    quantity_in = models.IntegerField(default=0)
    quantity_out = models.IntegerField(default=0)
    quantity_current = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.medicament.__str__()

    def update_quantity_in(self, quantity, previous_quantity):
        self.quantity_in += quantity - previous_quantity
        self.quantity_current = self.quantity_in - self.quantity_out
        self.save()

    def update_quantity_out(self, quantity):
        self.quantity_out += quantity
        self.quantity_current = self.quantity_in - self.quantity_out
        self.save()