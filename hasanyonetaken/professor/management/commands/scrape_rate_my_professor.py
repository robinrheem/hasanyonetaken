from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Scrape all ratings and comments of each professor"

    def handle(self, *args, **options):
        self.stdout.write("Hello World")
