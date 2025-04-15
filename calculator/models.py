from django.db import models
from applications.models import Application
from products.models import Product

class LoanCalculation(models.Model):
    """
    Stores the results of loan calculations for an application
    """
    INTEREST_TYPE_CHOICES = [
        ('fixed', 'Fixed Rate'),
        ('variable', 'Variable Rate'),
        ('interest_only', 'Interest Only'),
    ]
    
    COMPOUNDING_PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ]
    
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='calculation')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='calculations', null=True)
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPE_CHOICES)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Annual interest rate as percentage
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    loan_term_years = models.IntegerField()
    compounding_period = models.CharField(max_length=20, choices=COMPOUNDING_PERIOD_CHOICES, default='monthly')
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)
    total_payments = models.DecimalField(max_digits=12, decimal_places=2)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Calculation for {self.application}"
    
    class Meta:
        ordering = ['-created_at']


class RepaymentSchedule(models.Model):
    """
    Stores individual repayment entries for a loan calculation
    """
    calculation = models.ForeignKey(LoanCalculation, on_delete=models.CASCADE, related_name='repayments')
    payment_number = models.IntegerField()
    payment_date = models.DateField()
    payment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"Payment {self.payment_number} for {self.calculation.application}"
    
    class Meta:
        ordering = ['payment_number']


class Fee(models.Model):
    """
    Defines different types of fees that can be applied to loans
    """
    FEE_TYPE_CHOICES = [
        ('application', 'Application Fee'),
        ('establishment', 'Establishment Fee'),
        ('ongoing', 'Ongoing Fee'),
        ('late_payment', 'Late Payment Fee'),
        ('early_repayment', 'Early Repayment Fee'),
        ('other', 'Other Fee'),
    ]
    
    CALCULATION_METHOD_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Loan'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    calculation_method = models.CharField(max_length=20, choices=CALCULATION_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Fixed amount or percentage
    is_active = models.BooleanField(default=True)
    products = models.ManyToManyField(Product, related_name='calculator_fees', blank=True)
    calculations = models.ManyToManyField(LoanCalculation, through='ApplicationFee', related_name='fee_definitions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class ApplicationFee(models.Model):
    """
    Links fees to specific applications with their calculated amounts
    """
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='calculator_fees')
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='application_fees')
    calculation = models.ForeignKey(LoanCalculation, on_delete=models.SET_NULL, related_name='fees', null=True)
    calculated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_waived = models.BooleanField(default=False)
    waiver_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.fee.name} for {self.application}"
    
    class Meta:
        ordering = ['-created_at']
