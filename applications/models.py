from django.db import models
from borrowers.models import Borrower
from brokers.models import Broker
from products.models import Product
from django.conf import settings

class Valuer(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class QS(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Referral(models.Model):
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Application(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('funded', 'Funded'),
        ('closed', 'Closed'),
    )
    
    STAGE_CHOICES = (
        ('application', 'Application'),
        ('verification', 'Verification'),
        ('assessment', 'Assessment'),
        ('approval', 'Approval'),
        ('funding', 'Funding'),
        ('repayment', 'Repayment'),
    )
    
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='applications')
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='applications')
    valuer = models.ForeignKey(Valuer, on_delete=models.SET_NULL, related_name='applications', null=True, blank=True)
    qs = models.ForeignKey(QS, on_delete=models.SET_NULL, related_name='applications', null=True, blank=True)
    referral = models.ForeignKey(Referral, on_delete=models.SET_NULL, related_name='applications', null=True, blank=True)
    bdm = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='managed_applications', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='application')
    gross_loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    net_loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Application #{self.id} - {self.borrower}"
    
    class Meta:
        ordering = ['-created_at']

class Fee(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
    )
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='fees')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    invoice_path = models.FileField(upload_to='invoices/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.application}"
    
    class Meta:
        ordering = ['-created_at']

class Repayment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='repayments')
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    invoice_path = models.FileField(upload_to='repayment_invoices/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Repayment for {self.application} due on {self.due_date}"
    
    class Meta:
        ordering = ['due_date']

class LoanExtension(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='extensions')
    new_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    new_loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    new_repayment_schedule = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Extension for {self.application}"
    
    class Meta:
        ordering = ['-created_at']
