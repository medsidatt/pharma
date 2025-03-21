from django import forms
from .models import Alimentation
from django.core.exceptions import ValidationError
from datetime import datetime, date


class AlimentationForm(forms.ModelForm):
    class Meta:
        model = Alimentation
        fields = ['medicament', 'batch_number', 'quantity', 'purchase_price', 'expiry_date']

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')


        if expiry_date is None:
            ValidationError('Expiry date is required')
        if isinstance(expiry_date, datetime):
            expiry_date = expiry_date.date()

        # if expiry_date <= date.today():
        #     raise ValidationError("Expiry date must be greater than today's date.")

        return expiry_date

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_purchase_price(self):
        purchase_price = self.cleaned_data.get('purchase_price')
        if purchase_price <= 0:
            raise ValidationError("Purchase price must be greater than zero.")
        return purchase_price

    def clean_sell_price(self):
        medicament = self.cleaned_data.get('medicament')  # Get the related Medicament instance
        if medicament and medicament.sell_price <= 0:  # Ensure sell_price is valid for the Medicament instance
            raise ValidationError("Sell price for the selected medicament must be greater than zero.")
        return medicament.sell_price  # Optionally return the sell_price if needed for processing
