from decimal import Decimal
from datetime import date
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import LoanCalculation, RepaymentSchedule, Fee, ApplicationFee
from .serializers import (
    LoanCalculationSerializer, RepaymentScheduleSerializer,
    FeeSerializer, ApplicationFeeSerializer,
    LoanCalculatorInputSerializer, LoanCalculationResultSerializer
)
from .utils import (
    calculate_monthly_payment, calculate_interest_only_payment,
    generate_amortization_schedule, generate_interest_only_schedule,
    calculate_loan_summary, calculate_fee, calculate_total_cost
)
from applications.models import Application


class LoanCalculationViewSet(viewsets.ModelViewSet):
    queryset = LoanCalculation.objects.all()
    serializer_class = LoanCalculationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """
        Calculate loan details based on input parameters
        """
        input_serializer = LoanCalculatorInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        data = input_serializer.validated_data
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        loan_term_years = data['loan_term_years']
        interest_type = data['interest_type']
        compounding_period = data['compounding_period']
        start_date = data.get('start_date', date.today())
        application_id = data.get('application_id')
        
        # Calculate monthly payment based on interest type
        if interest_type == 'interest_only':
            monthly_payment = calculate_interest_only_payment(loan_amount, interest_rate)
            schedule = generate_interest_only_schedule(
                loan_amount, interest_rate, loan_term_years, start_date
            )
        else:
            monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, loan_term_years)
            schedule = generate_amortization_schedule(
                loan_amount, interest_rate, loan_term_years, start_date
            )
        
        # Calculate loan summary
        summary = calculate_loan_summary(schedule)
        
        # Prepare result data
        result_data = {
            'monthly_payment': monthly_payment,
            'total_payments': summary['total_payments'],
            'total_interest': summary['total_interest'],
            'total_principal': summary['total_principal'],
            'repayment_schedule': schedule,
            'interest_rate': interest_rate,
            'loan_term_years': loan_term_years,
            'loan_amount': loan_amount,
            'interest_type': interest_type,
            'compounding_period': compounding_period,
        }
        
        # If application ID is provided, calculate fees and save the calculation
        if application_id:
            application = get_object_or_404(Application, id=application_id)
            result_data['application_id'] = application_id
            
            # Calculate fees for this application
            fees = []
            product = application.product
            if product:
                for fee in product.fees.filter(is_active=True):
                    fee_amount = calculate_fee(
                        loan_amount, fee.fee_type, fee.amount, fee.calculation_method
                    )
                    fees.append({
                        'application': application.id,
                        'fee': fee.id,
                        'fee_name': fee.name,
                        'fee_type': fee.fee_type,
                        'calculated_amount': fee_amount,
                        'is_waived': False,
                        'waiver_reason': ''
                    })
            
            result_data['fees'] = fees
            
            # Calculate total cost including fees
            fee_amounts = [{'amount': fee['calculated_amount']} for fee in fees]
            total_cost = calculate_total_cost(
                loan_amount, summary['total_interest'], fee_amounts
            )
            result_data['total_cost'] = total_cost['total_cost']
            
            # Save the calculation to the database
            calculation = LoanCalculation.objects.create(
                application=application,
                interest_type=interest_type,
                interest_rate=interest_rate,
                loan_amount=loan_amount,
                loan_term_years=loan_term_years,
                compounding_period=compounding_period,
                monthly_payment=monthly_payment,
                total_payments=summary['total_payments'],
                total_interest=summary['total_interest']
            )
            
            # Save the repayment schedule
            for payment in schedule:
                RepaymentSchedule.objects.create(
                    calculation=calculation,
                    payment_number=payment['payment_number'],
                    payment_date=payment['payment_date'],
                    payment_amount=payment['payment_amount'],
                    principal_amount=payment['principal_amount'],
                    interest_amount=payment['interest_amount'],
                    remaining_balance=payment['remaining_balance']
                )
            
            # Save the fees
            for fee_data in fees:
                ApplicationFee.objects.create(
                    application=application,
                    fee_id=fee_data['fee'],
                    calculated_amount=fee_data['calculated_amount']
                )
        
        # Return the calculation results
        result_serializer = LoanCalculationResultSerializer(data=result_data)
        result_serializer.is_valid(raise_exception=True)
        return Response(result_serializer.data)


class RepaymentScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RepaymentSchedule.objects.all()
    serializer_class = RepaymentScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['calculation']


class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['fee_type', 'is_active', 'products']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'amount', 'created_at']


class ApplicationFeeViewSet(viewsets.ModelViewSet):
    queryset = ApplicationFee.objects.all()
    serializer_class = ApplicationFeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['application', 'fee', 'is_waived']
    
    @action(detail=True, methods=['post'])
    def waive(self, request, pk=None):
        """
        Waive a fee for an application
        """
        application_fee = self.get_object()
        application_fee.is_waived = True
        application_fee.waiver_reason = request.data.get('waiver_reason', '')
        application_fee.save()
        return Response(self.get_serializer(application_fee).data)
