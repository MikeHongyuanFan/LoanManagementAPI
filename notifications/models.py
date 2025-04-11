from django.db import models
from applications.models import Application
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('stage_change', 'Stage Change'),
        ('repayment_reminder', 'Repayment Reminder'),
        ('loan_maturity', 'Loan Maturity'),
        ('note_reminder', 'Note Reminder'),
        ('overdue_payment', 'Overdue Payment'),
        ('other', 'Other'),
    )
    
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    related_application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.TextField()
    trigger_date = models.DateTimeField()
    sent_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.recipient.username}"
    
    class Meta:
        ordering = ['-trigger_date']

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
