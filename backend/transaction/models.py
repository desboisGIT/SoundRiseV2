from django.db import models
from core.models import CustomUser
from django.db import models
from django.conf import settings

class Vendor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)  # Stripe vérifie le vendeur

    def __str__(self):
        return f"Vendeur: {self.user.username}"


from django.db import models
from beats.models import License  # ou Beat si on vend des beats directement
import uuid

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="cart")

    @property
    def total_price(self):
        """ Calcule le total du panier en tenant compte des quantités. """
        return sum(item.total_price for item in self.items.all())
    def __str__(self):
        return f"Panier de {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    license = models.OneToOneField(License, on_delete=models.CASCADE)  # Une seule occurrence par licence
    def __str__(self):
        return f"{self.license.title} - {self.license.price}€"
    
    @property
    def total_price(self):
        """ Calcule le total du panier en tenant compte des quantités. """
        return self.license.price

    


class Transaction(models.Model):
    PAYMENT_TYPES = [
        ('cart', 'Cart Purchase'),
        ('direct', 'Direct Purchase'),
        ('subscription', 'Subscription'),
        
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Prix total payé
    stripe_payment_id = models.CharField(max_length=255, blank=True, null=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='direct')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_type} - {self.user.username} - {self.total_amount}€ ({self.status})"


class TransactionItem(models.Model):
    """ Permet de stocker les détails d'un panier (plusieurs items par transaction). """
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="items")
    license = models.OneToOneField(License, on_delete=models.CASCADE)  # Une seule occurrence par licence    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_type} - {self.price}€"