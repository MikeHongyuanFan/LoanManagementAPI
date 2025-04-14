from rest_framework import serializers
from .models import Product, Fee
from decimal import Decimal

class FeeSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    
    class Meta:
        model = Fee
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_amount(self, value):
        """
        Validate that the amount is positive and, if a percentage, not greater than 100.
        """
        if value < 0:
            raise serializers.ValidationError("Fee amount cannot be negative.")
        
        # If this is a percentage fee, ensure it's not greater than 100%
        if self.initial_data.get('is_percentage', False) and value > 100:
            raise serializers.ValidationError("Percentage fee cannot exceed 100%.")
        
        return value

class ProductSerializer(serializers.ModelSerializer):
    fees = FeeSerializer(many=True, read_only=True)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    min_loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    max_loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_interest_rate(self, value):
        """
        Validate that the interest rate is positive and within a reasonable range.
        """
        if value < 0:
            raise serializers.ValidationError("Interest rate cannot be negative.")
        if value > 30:
            raise serializers.ValidationError("Interest rate cannot exceed 30%.")
        return value
    
    def validate_term_months(self, value):
        """
        Validate that the term months is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Term months must be positive.")
        return value
    
    def validate_min_credit_score(self, value):
        """
        Validate that the minimum credit score is within a reasonable range.
        """
        if value < 300 or value > 850:
            raise serializers.ValidationError("Credit score must be between 300 and 850.")
        return value
    
    def validate(self, data):
        """
        Validate that min_loan_amount is less than max_loan_amount.
        """
        min_loan = data.get('min_loan_amount', getattr(self.instance, 'min_loan_amount', 0) if self.instance else 0)
        max_loan = data.get('max_loan_amount', getattr(self.instance, 'max_loan_amount', 0) if self.instance else 0)
        
        if min_loan > max_loan:
            raise serializers.ValidationError({
                "non_field_errors": ["Minimum loan amount cannot be greater than maximum loan amount."]
            })
        
        return data
