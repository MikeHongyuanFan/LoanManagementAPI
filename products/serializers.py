from rest_framework import serializers
from .models import Product, Fee
from decimal import Decimal

class FeeSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    
    class Meta:
        model = Fee
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ProductSerializer(serializers.ModelSerializer):
    fees = FeeSerializer(many=True, read_only=True)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    min_loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    max_loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
