import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient, MeasurementUnit


class Command(BaseCommand):
    help = "Loads ingredients and their measurement units from CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        self.stdout.write("Process started")
        file_path = options["file_path"]
        ingredients = []
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            self.stdout.write(f"Opened {file_path}")
            reader = csv.reader(file, delimiter=",")
            for entry in reader:
                measurement_unit = MeasurementUnit.objects.get_or_create(name=entry[1])[
                    0
                ]
                ingredient = Ingredient(
                    name=entry[0], measurement_unit=measurement_unit
                )
                ingredients.append(ingredient)
                self.stdout.write(f"Entry {entry[0]}, {entry[1]} was parsed")

                if len(ingredients) > 999:
                    Ingredient.objects.bulk_create(ingredients)
                    self.stdout.write(f"{len(ingredients)} entries were bulk created")
                    ingredients = []

        if ingredients:
            Ingredient.objects.bulk_create(ingredients)
            self.stdout.write(f"{len(ingredients)} entries were bulk created")

        self.stdout.write("Process finished")
