from django.contrib import admin
from .models import Vendor, Cart, CartItem, Transaction, TransactionItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_account_id', 'is_verified')
    search_fields = ('user__username', 'stripe_account_id')
    list_filter = ('is_verified',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price')
    search_fields = ('user__username',)
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'license', 'total_price')
    search_fields = ('cart__user__username', 'license__title')
    list_filter = ('license__title',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'stripe_payment_id', 'payment_type', 'status', 'created_at')
    search_fields = ('user__username', 'stripe_payment_id', 'status')
    list_filter = ('payment_type', 'status', 'created_at')

@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'license', 'license__price')
    search_fields = ('transaction__user__username', 'license__title')
    list_filter = ('license__title',)



