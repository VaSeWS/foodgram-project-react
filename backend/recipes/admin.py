from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredientEntry, Tag, MeasurementUnit


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(RecipeIngredientEntry)
class RecipeIngredientEntryAdmin(admin.ModelAdmin):
    pass


class RecipeIngredientEntryInLine(admin.TabularInline):
    model = RecipeIngredientEntry
    list_display = ("ingredient", "amount")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "measurement_unit")


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = (
        ("author", "times_in_favourite"),
        "tags",
        "image",
        "name",
        "text",
        "cooking_time",
    )
    inlines = (RecipeIngredientEntryInLine, )
    readonly_fields = ("times_in_favourite", )
    list_display = (
        "name",
        "author",
    )
    list_filter = ("author__username", "name", "tags")
