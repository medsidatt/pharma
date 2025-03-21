# # medicaments/admin.py
# from django.contrib import admin
# from .models import Medicament, Stock
#
# @admin.register(Medicament)
# class MedicamentAdmin(admin.ModelAdmin):
#     list_display = ('name', 'price', 'category', 'current_stock')
#     list_filter = ('category',)
#     search_fields = ('name',)
#
# @admin.register(Stock)
# class StockAdmin(admin.ModelAdmin):
#     list_display = ('medicament', 'batch_number', 'creation_date', 'expiration_date', 'remaining_quantity', 'is_expired')
#     list_filter = ('medicament', 'creation_date', 'expiration_date')
#     search_fields = ('medicament__name', 'batch_number')