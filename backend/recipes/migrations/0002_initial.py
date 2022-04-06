# Generated by Django 4.0.3 on 2022-04-04 08:12

import django.db.models.deletion
import users.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("recipes", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                on_delete=models.SET(users.models.get_deleted_user),
                related_name="recipes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                through="recipes.RecipeIngredientEntry", to="recipes.ingredient"
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(to="recipes.tag"),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="measurement_unit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                to="recipes.measurementunit",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="ingredient",
            unique_together={("name", "measurement_unit")},
        ),
    ]