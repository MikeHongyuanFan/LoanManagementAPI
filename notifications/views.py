from rest_framework import viewsets, permissions, filters
from .models import Notification, Note
from .serializers import NotificationSerializer, NoteSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'sent_status', 'related_application']
    search_fields = ['message']
    ordering_fields = ['trigger_date', 'created_at']
    
    def get_queryset(self):
        # Only show notifications for the current user
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=False)
    def unread(self, request):
        unread = self.get_queryset().filter(sent_status=False)
        serializer = self.get_serializer(unread, many=True)
        return Response(serializer.data)

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
