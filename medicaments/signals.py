# # medicaments/signals.py
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from .models import Medicament, Stock
#
#
# @receiver(post_save, sender=Medicament)
# def update_stock_for_new_medicament(sender, instance, created, **kwargs):
#     """
#     Update stock when a new medicament is created.
#     """
#     if created:
#         # Add initial quantity to stock (e.g., 0)
#         stock, created = Stock.objects.get_or_create(medicament=instance)
#         stock.quantity_in += 0  # Set initial quantity here
#         stock.save()
#
#
# # medicaments/signals.py
# @receiver(post_save, sender=Medicament)
# def update_stock_for_updated_medicament(sender, instance, created, **kwargs):
#     """
#     Update stock when a medicament is updated.
#     """
#     if not created:
#         # Update stock if needed (e.g., if quantity changes)
#         stock = Stock.objects.filter(medicament=instance).first()
#         if stock:
#             # Example: Update stock based on changes to the medicament
#             stock.quantity_in = instance.initial_quantity  # Assuming `initial_quantity` is a field in Medicament
#             stock.save()
#
#
# @receiver(post_delete, sender=Medicament)
# def update_stock_for_deleted_medicament(sender, instance, **kwargs):
#     """
#     Update stock when a medicament is deleted.
#     """
#     stock = Stock.objects.filter(medicament=instance).first()
#     if stock:
#         # Set quantity_out to the total quantity_in
#         stock.quantity_out += stock.quantity_in
#         stock.save()