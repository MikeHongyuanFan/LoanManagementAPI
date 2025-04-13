"""
Signal handlers for dashboard app
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from applications.models import Application
from documents.models import Document
from borrowers.models import Borrower
from brokers.models import Broker
from products.models import Product

from .services import MetricAggregationService


@receiver(post_save, sender=Application)
@receiver(post_delete, sender=Application)
def update_application_metrics(sender, **kwargs):
    """
    Update application metrics when an application is created, updated, or deleted
    """
    MetricAggregationService.update_application_metrics()


@receiver(post_save, sender=Document)
@receiver(post_delete, sender=Document)
def update_document_metrics(sender, **kwargs):
    """
    Update document metrics when a document is created, updated, or deleted
    """
    MetricAggregationService.update_document_metrics()


@receiver(post_save, sender=Borrower)
@receiver(post_delete, sender=Borrower)
def update_borrower_metrics(sender, **kwargs):
    """
    Update borrower metrics when a borrower is created, updated, or deleted
    """
    MetricAggregationService.update_borrower_metrics()


@receiver(post_save, sender=Broker)
@receiver(post_delete, sender=Broker)
def update_broker_metrics(sender, **kwargs):
    """
    Update broker metrics when a broker is created, updated, or deleted
    """
    MetricAggregationService.update_broker_metrics()


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def update_product_metrics(sender, **kwargs):
    """
    Update product metrics when a product is created, updated, or deleted
    """
    MetricAggregationService.update_product_metrics()
