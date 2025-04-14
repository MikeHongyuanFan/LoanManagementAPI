from rest_framework import viewsets, permissions, filters, status
from .models import Notification, Note
from .serializers import NotificationSerializer, NoteSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import datetime
from rest_framework.exceptions import ValidationError

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'sent_status', 'related_application']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'trigger_date']
    
    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        
        # Handle date filtering
        created_after = self.request.query_params.get('created_after')
        created_before = self.request.query_params.get('created_before')
        
        if created_after:
            try:
                date_after = datetime.strptime(created_after, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_after)
            except ValueError:
                raise ValidationError({"created_after": ["Invalid date format. Use YYYY-MM-DD."]})
                
        if created_before:
            try:
                date_before = datetime.strptime(created_before, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_before)
            except ValueError:
                raise ValidationError({"created_before": ["Invalid date format. Use YYYY-MM-DD."]})
        
        # Validate type parameter
        type_param = self.request.query_params.get('type')
        if type_param and type_param not in [choice[0] for choice in Notification.NOTIFICATION_TYPES]:
            raise ValidationError({"type": [f"Invalid notification type. Must be one of: {', '.join([choice[0] for choice in Notification.NOTIFICATION_TYPES])}."]})
                
        return queryset
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        unread = self.get_queryset().filter(sent_status=False)
        serializer = self.get_serializer(unread, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        unread_count = self.get_queryset().filter(sent_status=False).count()
        return Response({'unread_count': unread_count})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        if request.data and len(request.data) > 0:
            # If there's any data in the request, it's invalid for this endpoint
            return Response({"detail": "This endpoint does not accept any parameters."}, 
                           status=status.HTTP_400_BAD_REQUEST)
            
        unread = self.get_queryset().filter(sent_status=False)
        count = unread.count()
        unread.update(sent_status=True)
        return Response({'marked_count': count})

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['application', 'user', 'reminder_date']
    search_fields = ['content']
    ordering_fields = ['created_at', 'reminder_date']
    
    def get_queryset(self):
        return Note.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def validate_reminder_date(self, reminder_date):
        """
        Validate that the reminder date is in the future.
        """
        if reminder_date and reminder_date < timezone.now():
            raise ValidationError({"reminder_date": ["Reminder date must be in the future."]})
        return reminder_date
