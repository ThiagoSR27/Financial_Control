from django.contrib import admin
from .models import Category, Transaction, Account, AccountHistory

# Register your models here.
#Configurando categoria

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    search_fields = ('name',)
    list_filter = ('type',)
    
#Configuração para Transação    

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'value', 'date', 'category')
    list_filter = ('date', 'category', 'category__type')
    search_fields = ('description',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)

@admin.register(AccountHistory)
class AccountHistoryAdmin(admin.ModelAdmin):
    list_display = ('account', 'value', 'type', 'date', 'description')
    list_filter = ('account', 'type', 'date', 'description')
