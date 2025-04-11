"""
Management command to check for documents that are about to expire
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

from documents.models import Document
from documents.utils.notification_manager import DocumentNotificationManager

class Command(BaseCommand):
    help = 'Check for documents that are about to expire and send notifications'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days before expiration to send notifications'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        
        # Calculate the date range
        today = timezone.now().date()
        expiration_date = today + timezone.timedelta(days=days)
        
        # Find documents expiring within the specified days
        expiring_documents = Document.objects.filter(
            Q(expiration_date__gte=today) & 
            Q(expiration_date__lte=expiration_date) &
            Q(is_latest_version=True)
        )
        
        self.stdout.write(f"Found {expiring_documents.count()} documents expiring within {days} days")
        
        # Send notifications
        notification_manager = DocumentNotificationManager()
        
        for document in expiring_documents:
            days_remaining = (document.expiration_date - today).days
            
            try:
                notification_manager.notify_document_expiring_soon(document, days_remaining)
                self.stdout.write(self.style.SUCCESS(
                    f"Sent notification for document '{document.title}' (ID: {document.id}) expiring in {days_remaining} days"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Failed to send notification for document '{document.title}' (ID: {document.id}): {str(e)}"
                ))
        
        self.stdout.write(self.style.SUCCESS('Document expiration check completed'))
