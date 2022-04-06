import csv
import logging
from django.core.management import BaseCommand

from recipes.models import Ingredient, MeasurementUnit


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


class Command(BaseCommand):
    help = "Loads ingredients and their measurement units from CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        logger.info("Process started")
        file_path = options["file_path"]
        ingredients = []
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            logger.info("Opened %s", file_path)
            reader = csv.reader(file, delimiter=',')
            for entry in reader:
                measurement_unit = MeasurementUnit.objects.get_or_create(
                    name=entry[1]
                )[0]
                ingredient = Ingredient(
                    name=entry[0],
                    measurement_unit=measurement_unit
                )
                ingredients.append(ingredient)
                logger.info("Entry %s, %s was parsed", *entry)

                if len(ingredients) > 999:
                    Ingredient.objects.bulk_create(ingredients)
                    logger.info("%i entries were bulk created", len(ingredients))
                    ingredients = []

        if ingredients:
            Ingredient.objects.bulk_create(ingredients)
            logger.info("%i entries were bulk created", len(ingredients))

        logger.info("Process finished")
