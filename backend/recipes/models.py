from django.contrib.auth import get_user_model
from django.db import models

from users.models import get_deleted_user


class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=200)  # TODO: add hex value validator
    slug = models.SlugField()

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ("id",)

    def __str__(self):
        return self.name


class MeasurementUnit(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Measurement Unit"
        verbose_name_plural = "Measurement Units"
        ordering = ("id",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    measurement_unit = models.ForeignKey(MeasurementUnit, on_delete=models.RESTRICT)

    class Meta:
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"
        ordering = ("name",)
        unique_together = ("name", "measurement_unit")

    def __str__(self):
        return self.name


class RecipeIngredientEntry(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    recipe = models.ForeignKey(
        "recipes.Recipe", on_delete=models.CASCADE, related_name="ingredient_entries"
    )
    amount = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Recipe ingredient entry"
        verbose_name_plural = "Recipe ingredient entries"
        ordering = ("id",)

    def __str__(self):
        return self.ingredient.name


class Recipe(models.Model):
    author = models.ForeignKey(
        get_user_model(), on_delete=models.SET(get_deleted_user), related_name="recipes"
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="recipes.RecipeIngredientEntry"
    )
    tags = models.ManyToManyField(Tag)
    image = models.ImageField()
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ("-created",)

    def __str__(self):
        return self.name

    @property
    def times_in_favourite(self):
        return self.in_favourites.count()
