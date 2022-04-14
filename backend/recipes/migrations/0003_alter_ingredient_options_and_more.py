# Generated by Django 4.0.3 on 2022-04-08 19:34

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ingredient",
            options={
                "ordering": ("name",),
                "verbose_name": "Ingredient",
                "verbose_name_plural": "Ingredients",
            },
        ),
        migrations.AlterModelOptions(
            name="measurementunit",
            options={
                "ordering": ("id",),
                "verbose_name": "Measurement Unit",
                "verbose_name_plural": "Measurement Units",
            },
        ),
        migrations.AlterModelOptions(
            name="recipe",
            options={
                "ordering": ("-created",),
                "verbose_name": "Recipe",
                "verbose_name_plural": "Recipes",
            },
        ),
        migrations.AlterModelOptions(
            name="recipeingrediententry",
            options={
                "ordering": ("id",),
                "verbose_name": "Recipe ingredient entry",
                "verbose_name_plural": "Recipe ingredient entries",
            },
        ),
        migrations.AlterModelOptions(
            name="tag",
            options={
                "ordering": ("id",),
                "verbose_name": "Tag",
                "verbose_name_plural": "Tags",
            },
        ),
        migrations.AddField(
            model_name="recipe",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="recipeingrediententry",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredient_entries",
                to="recipes.recipe",
            ),
        ),
    ]