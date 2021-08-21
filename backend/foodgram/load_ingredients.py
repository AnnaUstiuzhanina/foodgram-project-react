import json
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")
django.setup()

from recipes.models import Ingredient



def load_ingredients_from_json():
    db_objects = []
    with open('ingredients.json') as f:
        data = json.load(f)

        for ingredient_data in data:
            db_objects.append(
                Ingredient(**ingredient_data)
            )

    Ingredient.objects.bulk_create(db_objects)


load_ingredients_from_json()
