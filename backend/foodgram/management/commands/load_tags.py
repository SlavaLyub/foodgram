import csv

from django.core.management.base import BaseCommand

from foodgram.models import Tag


class Command(BaseCommand):
    help = 'Loads tags from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file',
                            type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['name'].strip()
                slug = row['slug'].strip()

                tag, created = Tag.objects.get_or_create(name=name,
                                                         slug=slug)
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f"Added: {name} ({slug})")
                    )
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Skipped (already exists): {name} ({slug})")
                    )
