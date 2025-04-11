from rest_framework import serializers
from .models import Borrower

class BorrowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrower
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
