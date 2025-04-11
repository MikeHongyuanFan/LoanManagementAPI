from rest_framework import serializers
from .models import Notification, Note

class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'type_display')

class NoteSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user_name')
