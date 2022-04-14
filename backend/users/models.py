from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


def get_deleted_user():
    return get_user_model().objects.get_or_create(username="deleted")[0]


class User(AbstractUser):
    shopping_list = models.ManyToManyField(
        "recipes.Recipe",
        related_name="in_shopping_list",
        blank=True,
    )
    favourite = models.ManyToManyField(
        "recipes.Recipe",
        related_name="in_favourites",
        blank=True,
    )
    followed_to = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
    )

    class Meta:
        constraints = (
            models.CheckConstraint(
                check=~models.Q(username__iexact="me"), name="username_is_not_me"
            ),
        )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name", "password", "username")
