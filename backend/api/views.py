from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredientEntry
from rest_framework.views import APIView

from .permissions import IsStaffOrReadOnly, IsStaffOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, TagSerializer,
                          UserSubscriptionSerializer,
                          RecipeCreateSerializer)


@api_view(["GET", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def subscribe(request, uid):
    author = get_object_or_404(get_user_model(), id=uid)
    user = request.user
    serializer = UserSubscriptionSerializer(author, context={"user": user})
    in_followed = user.followed_to.filter(id=author.id).exists()
    if request.method == "GET":
        if not in_followed:
            user.followed_to.add(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == "DELETE":
        if in_followed:
            user.followed_to.remove(author)
            return Response(status=status.HTTP_204_NO_CONTENT)

    error_message_part = (
        "already subscribed" if request.method == "GET" else "not subscribed"
    )
    return Response(
        {"errors": f"You're {error_message_part} to this author"},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def subscriptions(request):
    user = request.user
    serializer = UserSubscriptionSerializer(
        user.followed_to, context={"user": user}, many=True
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsStaffOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().select_related()
    serializer_class = IngredientSerializer
    permission_classes = (IsStaffOrReadOnly,)

    def get_queryset(self):
        name = self.request.query_params.get("name", None)
        if name:
            return Ingredient.objects.filter(
                name__istartswith=name
            ).select_related()
        return Ingredient.objects.all().select_related()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related()
    permission_classes = (IsStaffOwnerOrReadOnly,)
    http_method_names = ('get', 'post', 'delete', 'put')

    def get_queryset(self):
        result = Recipe.objects.all().prefetch_related()
        user = self.request.user
        is_favorited = self.request.query_params.get("is_favorited", "0")
        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart", "0")
        author = self.request.query_params.get("author")
        # If multiple tags were given as tags=lunch&tags=breakfast
        # only the last one is taken without casting to dict.
        tags = dict(self.request.query_params).get("tags", [])
        if author:
            result = result.filter(author=author)
        if tags:
            result = result.filter(tags__name__in=tags)
        if int(is_favorited):
            result = result.intersection(user.favourite.all())
        if int(is_in_shopping_cart):
            result = result.intersection(user.shopping_list.all())
        return result

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(
        methods=("GET", "DELETE"),
        detail=False,
        url_path=r"(?P<recipe_id>\d+)/favorite",
        serializer_class=RecipeShortSerializer,
    )
    def favorite(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer = self.get_serializer(recipe)
        recipe_in_favorite = user.favourite.filter(id=recipe.id).exists()
        if request.method == "GET":
            if not recipe_in_favorite:
                user.favourite.add(recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if recipe_in_favorite:
                user.favourite.remove(recipe)
                return Response(status=status.HTTP_204_NO_CONTENT)

        error_msg_part = "is already" if request.method == "GET" else "is not"
        return Response(
            {"errors": f"Recipe {error_msg_part} in favourites"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=("GET", "DELETE"),
        detail=False,
        url_path=r"(?P<recipe_id>\d+)/shopping_cart",
        serializer_class=RecipeShortSerializer,
    )
    def shopping_cart(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer = self.get_serializer(recipe)
        recipe_in_cart = user.shopping_list.filter(id=recipe.id).exists()
        if request.method == "GET":
            if not recipe_in_cart:
                user.shopping_list.add(recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if recipe_in_cart:
                user.shopping_list.remove(recipe)
                return Response(status=status.HTTP_204_NO_CONTENT)

        error_msg_part = "is already" if request.method == "GET" else "is not"
        return Response(
            {"errors": f"Recipe {error_msg_part} in shopping cart"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        shopping_list = {}
        user = request.user
        ingredients = user.shopping_list.values_list(
            'ingredient_entries__ingredient__name',
            'ingredient_entries__amount',
            'ingredient_entries__ingredient__measurement_unit__name')
        ingredients = ingredients.values(
            'ingredient_entries__ingredient__name',
            'ingredient_entries__ingredient__measurement_unit__name'
        ).annotate(total=Sum('ingredient_entries__amount'))
        for ingredient in ingredients:
            amount = ingredient['total']
            name = ingredient['ingredient_entries__ingredient__name']
            measurement_unit = ingredient[
                'ingredient_entries__ingredient__measurement_unit__name'
            ]
            shopping_list[name] = {
                'measurement_unit': measurement_unit,
                'amount': amount
            }
        to_buy = []
        for item in shopping_list:
            to_buy.append(
                f'{item}      {shopping_list[item]["amount"]} '
                f'{shopping_list[item]["measurement_unit"]} \n'
            )

        response = HttpResponse(to_buy, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="to_buy.txt"'
        return response
