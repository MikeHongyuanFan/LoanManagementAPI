from django.db import models
from applications.models import Application
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('system', 'System'),
        ('email', 'Email'),
        ('alert', 'Alert'),
        ('stage_change', 'Stage Change'),
        ('repayment_reminder', 'Repayment Reminder'),
        ('loan_maturity', 'Loan Maturity'),
        ('note_reminder', 'Note Reminder'),
        ('overdue_payment', 'Overdue Payment'),
        ('other', 'Other'),
    )
    
    # Renamed from recipient to user
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255, default="Notification")
    message = models.TextField()
    # Renamed from type to notification_type
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    related_application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    # Renamed from sent_status to is_read
    sent_status = models.BooleanField(default=False)
    trigger_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.recipient.username}"
    
    class Meta:
        ordering = ['-created_at']

class Note(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    reminder_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Note by {self.user.username} on {self.application}"
    
    class Meta:
        ordering = ['-created_at']
