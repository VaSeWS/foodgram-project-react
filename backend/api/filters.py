from django import forms
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class NonValidatingMultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        pass


class CustomFilter(filters.AllValuesMultipleFilter):
    field_class = NonValidatingMultipleChoiceField


class RecipeFilter(filters.FilterSet):
    tags = CustomFilter(field_name="tags__slug")
    is_favorited = filters.BooleanFilter(method="get_favorite")
    is_in_shopping_cart = filters.BooleanFilter(method="get_in_shopping_cart")

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(in_favourites=self.request.user)
        return queryset

    def get_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(in_shopping_list=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("tags", "author")
