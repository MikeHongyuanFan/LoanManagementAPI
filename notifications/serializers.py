from rest_framework import serializers
from .models import Notification, Note

class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'type_display', 'recipient_name')
    
    def validate_title(self, value):
        """
        Validate that the title is not empty and not too long.
        """
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return value
    
    def validate_type(self, value):
        """
        Validate that the notification type is a valid choice.
        """
        valid_types = [choice[0] for choice in Notification.NOTIFICATION_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Type must be one of: {', '.join(valid_types)}")
        return value
    
    def validate_message(self, value):
        """
        Validate that the message is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value

class NoteSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user_name')
    
    def validate_content(self, value):
        """
        Validate that the content is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value
    
    def validate_reminder_date(self, value):
        """
        Validate that the reminder date is in the future.
        """
        if value and value < serializers.DateTimeField().to_representation(serializers.DateTimeField().to_internal_value('now')):
            raise serializers.ValidationError("Reminder date must be in the future.")
        return value
