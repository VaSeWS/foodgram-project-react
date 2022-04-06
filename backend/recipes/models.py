from django.contrib.auth import get_user_model
from django.db import models
from users.models import get_deleted_user


class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=200)  # TODO: add hex value validator
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("id",)


class MeasurementUnit(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("id",)


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    measurement_unit = models.ForeignKey(MeasurementUnit, on_delete=models.RESTRICT)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        unique_together = ("name", "measurement_unit")


class RecipeIngredientEntry(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    recipe = models.ForeignKey(
        "recipes.Recipe", on_delete=models.CASCADE, related_name="ingredient_entries"
    )
    amount = models.PositiveIntegerField()

    def __str__(self):
        return self.ingredient.name

    class Meta:
        verbose_name_plural = "Recipe ingredient entries"
        ordering = ("id",)


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

    def __str__(self):
        return self.name

    @property
    def times_in_favourite(self):
        return self.in_favourites.count()

    class Meta:
        ordering = ("-created",)
