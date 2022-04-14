from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCart, IngredientViewSet, ListFollowViewSet,
                    RecipeViewSet, TagViewSet, subscribe)

router = DefaultRouter()
router.register(r"tags", TagViewSet)
router.register(r"ingredients", IngredientViewSet)
router.register(r"recipes", RecipeViewSet, basename="recipes")


urlpatterns = (
    path("users/subscriptions/", ListFollowViewSet.as_view()),
    path("users/<int:uid>/subscribe/", subscribe),
    path(
        "recipes/download_shopping_cart/",
        DownloadShoppingCart.as_view(),
        name="download_shopping_cart",
    ),
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
)
