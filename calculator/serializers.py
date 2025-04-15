from rest_framework import serializers
from .models import LoanCalculation, RepaymentSchedule, Fee, ApplicationFee
from django.utils import timezone
from decimal import Decimal


class RepaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepaymentSchedule
        fields = [
            'id', 'payment_number', 'payment_date', 'payment_amount',
            'principal_amount', 'interest_amount', 'remaining_balance'
        ]


class LoanCalculationSerializer(serializers.ModelSerializer):
    repayments = RepaymentScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = LoanCalculation
        fields = [
            'id', 'application', 'interest_type', 'interest_rate',
            'loan_amount', 'loan_term_years', 'compounding_period',
            'monthly_payment', 'total_payments', 'total_interest',
            'created_at', 'updated_at', 'repayments'
        ]
    
    def validate_loan_amount(self, value):
        """Validate that loan amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be greater than zero.")
        return value
    
    def validate_interest_rate(self, value):
        """Validate that interest rate is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Interest rate cannot be negative.")
        return value
    
    def validate_loan_term_years(self, value):
        """Validate that loan term is positive and reasonable"""
        if value <= 0:
            raise serializers.ValidationError("Loan term must be greater than zero.")
        if value > 40:
            raise serializers.ValidationError("Loan term cannot exceed 40 years.")
        return value


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = [
            'id', 'name', 'description', 'fee_type', 'calculation_method',
            'amount', 'is_active', 'products', 'created_at', 'updated_at'
        ]
    
    def validate_name(self, value):
        """Validate that name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Fee name cannot be empty.")
        return value
    
    def validate_amount(self, value):
        """Validate that amount is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Fee amount cannot be negative.")
        return value
    
    def validate_fee_type(self, value):
        """Validate that fee_type is one of the allowed choices"""
        allowed_types = [choice[0] for choice in Fee.FEE_TYPE_CHOICES]
        if value not in allowed_types:
            raise serializers.ValidationError(f"Fee type must be one of: {', '.join(allowed_types)}")
        return value
    
    def validate_calculation_method(self, value):
        """Validate that calculation_method is one of the allowed choices"""
        allowed_methods = [choice[0] for choice in Fee.CALCULATION_METHOD_CHOICES]
        if value not in allowed_methods:
            raise serializers.ValidationError(f"Calculation method must be one of: {', '.join(allowed_methods)}")
        return value


class ApplicationFeeSerializer(serializers.ModelSerializer):
    fee_name = serializers.CharField(source='fee.name', read_only=True)
    fee_type = serializers.CharField(source='fee.fee_type', read_only=True)
    
    class Meta:
        model = ApplicationFee
        fields = [
            'id', 'application', 'fee', 'fee_name', 'fee_type',
            'calculated_amount', 'is_waived', 'waiver_reason',
            'created_at', 'updated_at'
        ]
    
    def validate_calculated_amount(self, value):
        """Validate that calculated amount is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Calculated amount cannot be negative.")
        return value
    
    def validate(self, data):
        """Validate that waiver_reason is provided if is_waived is True"""
        is_waived = data.get('is_waived', False)
        waiver_reason = data.get('waiver_reason', '')
        
        if is_waived and not waiver_reason.strip():
            raise serializers.ValidationError({"waiver_reason": "Waiver reason is required when waiving a fee."})
        
        return data


class LoanCalculatorInputSerializer(serializers.Serializer):
    """
    Serializer for loan calculator input parameters
    """
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    loan_term_years = serializers.IntegerField(min_value=1, max_value=40)
    interest_type = serializers.ChoiceField(
        choices=['fixed', 'variable', 'interest_only'],
        default='fixed'
    )
    compounding_period = serializers.ChoiceField(
        choices=['daily', 'monthly', 'quarterly', 'annually'],
        default='monthly'
    )
    start_date = serializers.DateField(required=False)
    application_id = serializers.IntegerField(required=False)
    
    def validate_loan_amount(self, value):
        """Validate that loan amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be greater than zero.")
        return value
    
    def validate_interest_rate(self, value):
        """Validate that interest rate is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Interest rate cannot be negative.")
        return value


class LoanCalculationResultSerializer(serializers.Serializer):
    """
    Serializer for loan calculation results
    """
    monthly_payment = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_payments = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_interest = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_principal = serializers.DecimalField(max_digits=12, decimal_places=2)
    repayment_schedule = serializers.ListField(child=serializers.DictField())
    
    # Additional fields for comprehensive results
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    loan_term_years = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_type = serializers.CharField()
    compounding_period = serializers.CharField()
    
    # Optional fields if application is provided
    application_id = serializers.IntegerField(required=False)
    calculation_id = serializers.IntegerField(required=False)
    fees = serializers.ListField(child=serializers.DictField(), required=False)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
