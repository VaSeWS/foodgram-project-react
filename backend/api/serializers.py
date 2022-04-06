from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredientEntry, Tag
from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name", "is_subscribed")

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user

        return (
            user.followed_to.filter(id=obj.id).exists()
            if not user.is_anonymous
            else False
        )


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source="measurement_unit.name")

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id", "name", "measurement_unit")


class RecipeIngredientEntrySerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit.name"
    )

    class Meta:
        model = RecipeIngredientEntry
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = ("name", "measurement_unit")


class RecipeIngredientEntryCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredientEntry
        fields = ("id", "amount")


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientEntrySerializer(
        source="ingredient_entries", many=True
    )
    image = Base64ImageField()

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.favourite.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.shopping_list.filter(id=obj.id).exists()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "id",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientEntryCreateSerializer(
        many=True,
    )
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        ingredients_ids = []
        if len(ingredients) == 0:
            raise serializers.ValidationError(
                "There must be at least one ingredient in the recipe."
            )
        for item in ingredients:
            try:
                amount = int(item.get("amount"))
            except ValueError:
                raise serializers.ValidationError("'amount' must be an integer.")
            if amount <= 0:
                raise serializers.ValidationError(
                    "Ingredient amount must be a positive integer."
                )
            elif item["id"] in ingredients_ids:
                raise serializers.ValidationError(
                    "Ingredients must be unique in one recipe."
                )
            else:
                ingredients_ids.append(item["id"])
        return data

    def validate_tags(self, data):
        tags = self.initial_data.get("tags")
        if len(tags) == 0:
            raise serializers.ValidationError("There must be at least one tag.")
        unique_id_tags = dict()
        for item in tags:
            pk = item
            if pk in unique_id_tags:
                raise serializers.ValidationError("Tags must be unique.")
            unique_id_tags[pk] = 0
        return data

    def validate_cooking_time(self, data):
        try:
            cooking_time = float(data)
        except ValueError:
            raise serializers.ValidationError("Cooking time must be an integer.")
        if cooking_time <= 0:
            raise serializers.ValidationError(
                "Cooking time must be a positive integer."
            )
        return data

    def add_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def add_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_entry = ingredient["id"]
            amount = ingredient["amount"]
            recipe.ingredient_entries.create(ingredient=ingredient_entry, amount=amount)

    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")
        author = self.context.get("request").user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_ingredient(ingredients_data, recipe)
        self.add_tags(tags_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags")
        ingredient_data = validated_data.pop("ingredients")
        instance.tags.clear()
        self.add_tags(tags_data, instance)
        instance.ingredients.clear()
        self.add_ingredient(ingredient_data, instance)
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    # def create(self, validated_data):
    #     ingredient_entries = validated_data.pop("ingredients")
    #     tags = validated_data.pop("tags")
    #     recipe = Recipe.objects.create(
    #         **validated_data,
    #     )
    #     for tag in tags:
    #         recipe.tags.add(tag)
    #     for data in ingredient_entries:
    #         recipe.ingredient_entries.create(
    #             ingredient=Ingredient.objects.get(**data["ingredient"]),
    #             amount=data["amount"]
    #         )
    #
    #     return recipe


class UserSubscriptionSerializer(UserSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
        )

    def get_is_subscribed(self, obj):
        print(self.context)
        user = self.context.get("user")

        return (
            user.followed_to.filter(id=obj.id).exists()
            if not user.is_anonymous
            else False
        )
