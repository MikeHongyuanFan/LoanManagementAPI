from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    term_months = models.IntegerField(default=360)
    min_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, default=50000)
    max_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, default=1000000)
    min_credit_score = models.IntegerField(default=650)
    is_active = models.BooleanField(default=True)
    document_path = models.FileField(upload_to='product_documents/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Fee(models.Model):
    product = models.ForeignKey(Product, related_name='fees', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_percentage = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.product.name}"
    
    class Meta:
        ordering = ['name']
