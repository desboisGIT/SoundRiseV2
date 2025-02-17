from rest_framework import serializers
from .models import Vendor

class StripeAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['stripe_account_id']
