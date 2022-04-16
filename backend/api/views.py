from django.contrib.auth import get_user_model
from django.db.models import Exists, Sum, Value, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Ingredient, Recipe, Tag

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsStaffOrReadOnly, IsStaffOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          TagSerializer, UserSubscriptionSerializer)

User = get_user_model()


@api_view(["GET", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def subscribe(request, uid):
    author = get_object_or_404(User, id=uid)
    user = request.user
    serializer = UserSubscriptionSerializer(
        author,
        context={
            "user": user,
            "request": request,
        },
    )
    in_followed = user.followed_to.filter(id=author.id).exists()
    error_message_part = (
        "already subscribed" if request.method == "GET" else "not subscribed"
    )
    if request.method == "GET" and not in_followed:
        user.followed_to.add(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == "DELETE" and in_followed:
        user.followed_to.remove(author)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {"errors": f"You're {error_message_part} to this author"},
        status=status.HTTP_400_BAD_REQUEST,
    )


class ListFollowViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = UserSubscriptionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "user": self.request.user})
        return context

    def get_queryset(self):
        return self.request.user.followed_to.prefetch_related()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsStaffOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.select_related()
    serializer_class = IngredientSerializer
    permission_classes = (IsStaffOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related()
    permission_classes = (IsStaffOwnerOrReadOnly,)
    http_method_names = ("get", "post", "delete", "put", "patch")
    # Frontend sends PATCH request on recipe update
    # instead of PUT as it is in the api docs
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.prefetch_related().annotate(
            is_favorited=(
                Exists(user.favourite.filter(id=OuterRef("id")))
                if user.is_authenticated
                else Value(False)
            ),
            is_in_shopping_cart=(
                Exists(user.shopping_list.filter(id=OuterRef("id")))
                if user.is_authenticated
                else Value(False)
            ),
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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
        error_msg_part = "is already" if request.method == "GET" else "is not"
        if request.method == "GET" and not recipe_in_favorite:
            user.favourite.add(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE" and recipe_in_favorite:
            user.favourite.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

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
        error_msg_part = "is already" if request.method == "GET" else "is not"
        if request.method == "GET" and not recipe_in_cart:
            user.shopping_list.add(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE" and recipe_in_cart:
            user.shopping_list.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"errors": f"Recipe {error_msg_part} in shopping cart"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        shopping_list = {}
        user = request.user
        ingredients = user.shopping_list.values(
            "ingredient_entries__ingredient__name",
            "ingredient_entries__ingredient__measurement_unit__name",
        ).annotate(total=Sum("ingredient_entries__amount"))
        for ingredient in ingredients:
            amount = ingredient["total"]
            name = ingredient["ingredient_entries__ingredient__name"]
            measurement_unit = ingredient[
                "ingredient_entries__ingredient__measurement_unit__name"
            ]
            shopping_list[name] = {
                "measurement_unit": measurement_unit,
                "amount": amount,
            }
        to_buy = []
        for item in shopping_list:
            to_buy.append(
                f'{item}      {shopping_list[item]["amount"]} '
                f'{shopping_list[item]["measurement_unit"]} \n'
            )

        response = HttpResponse(to_buy, "Content-Type: text/plain")
        response["Content-Disposition"] = 'attachment; filename="to_buy.txt"'
        return response
