import csv
from django.core.management.base import BaseCommand
from foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'Loads ingredients from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file',
                            type=str,
                            help='The path to the CSV file'
                            )

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    name, unit = row
                    name = name.strip()
                    unit = unit.strip()

                    ingredient, created = Ingredient.objects.get_or_create(
                        name=name, unit=unit
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(
                            f"Added: {name} ({unit})")
                        )
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"Skipped (already exists): {name} ({unit})")
                        )
                else:
                    self.stdout.write(self.style.ERROR(
                        f"Skipped (invalid format): {row}")
                    )
