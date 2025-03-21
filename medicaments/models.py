from django.db import models

from utils.enums.enums import PrescriptionRequiredEnum


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Medicament(models.Model):
    name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False)
    dosage = models.CharField(max_length=50, null=False)
    unit_type = models.CharField(max_length=50, null=False)
    manufacturer = models.CharField(max_length=255, null=False)
    storage_conditions = models.CharField(max_length=255, null=False)
    is_prescription_required = models.CharField(
        max_length=3, choices=PrescriptionRequiredEnum.choices(), default=PrescriptionRequiredEnum.NO.value
    )
    image = models.ImageField(upload_to='medicaments/%Y/%m/%d/', blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.unit_type} - {self.dosage} "

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def toJson(self):
        return {
            'name': self.name,
            'generic_name': self.generic_name,
            'category': self.category.name if self.category else None,
            'dosage': self.dosage,
            'unit_type': self.unit_type,
            'manufacturer': self.manufacturer,
            'storage_conditions': self.storage_conditions,
            'is_prescription_required': self.is_prescription_required,
            'purchase_price': str(self.purchase_price),
            'selling_price': str(self.selling_price),
        }

    def update_prices(self, purchase_price, selling_price):
        self.purchase_price = purchase_price
        self.selling_price = selling_price
        self.save()