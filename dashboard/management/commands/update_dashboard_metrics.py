from django.core.management.base import BaseCommand
from dashboard.services import MetricAggregationService


class Command(BaseCommand):
    help = 'Updates all dashboard metrics'

    def handle(self, *args, **options):
        self.stdout.write('Updating dashboard metrics...')
        
        try:
            MetricAggregationService.update_all_metrics()
            self.stdout.write(self.style.SUCCESS('Successfully updated dashboard metrics'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating dashboard metrics: {str(e)}'))
