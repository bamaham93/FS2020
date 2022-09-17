from django.contrib import admin
from .models import Transaction, Category

# Register your models here.
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Category)
class CatgoryAdmin(admin.ModelAdmin):
    """
    """
