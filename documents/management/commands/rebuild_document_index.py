"""
Management command to rebuild the document search index
"""
from django.core.management.base import BaseCommand
from haystack.management.commands import rebuild_index

class Command(BaseCommand):
    help = 'Rebuilds the document search index'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting document index rebuild...'))
        
        # Call the haystack rebuild_index command
        command = rebuild_index.Command()
        command.handle(
            using=['default'],
            noinput=True,
            remove=True,
            verbosity=2,
            workers=1
        )
        
        self.stdout.write(self.style.SUCCESS('Document index rebuild complete!'))
