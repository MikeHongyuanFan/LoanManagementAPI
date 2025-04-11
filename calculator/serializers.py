from rest_framework import serializers
from .models import LoanCalculation, RepaymentSchedule, Fee, ApplicationFee


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


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = [
            'id', 'name', 'description', 'fee_type', 'calculation_method',
            'amount', 'is_active', 'products', 'created_at', 'updated_at'
        ]


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


class LoanCalculationResultSerializer(serializers.Serializer):
    """
    Serializer for loan calculation results
    """
    monthly_payment = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_payments = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_interest = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_principal = serializers.DecimalField(max_digits=12, decimal_places=2)
    repayment_schedule = RepaymentScheduleSerializer(many=True)
    
    # Additional fields for comprehensive results
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    loan_term_years = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_type = serializers.CharField()
    compounding_period = serializers.CharField()
    
    # Optional fields if application is provided
    application_id = serializers.IntegerField(required=False)
    fees = ApplicationFeeSerializer(many=True, required=False)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
