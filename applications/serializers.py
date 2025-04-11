from rest_framework import serializers
from .models import Application, Valuer, QS, Referral, Fee, Repayment, LoanExtension

class ValuerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valuer
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class QSSerializer(serializers.ModelSerializer):
    class Meta:
        model = QS
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class LoanExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanExtension
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ApplicationSerializer(serializers.ModelSerializer):
    fees = FeeSerializer(many=True, read_only=True)
    repayments = RepaymentSerializer(many=True, read_only=True)
    extensions = LoanExtensionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ApplicationDetailSerializer(ApplicationSerializer):
    valuer = ValuerSerializer(read_only=True)
    qs = QSSerializer(read_only=True)
    referral = ReferralSerializer(read_only=True)
    
    class Meta(ApplicationSerializer.Meta):
        depth = 1
