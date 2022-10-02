from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from recipes.serializer_fields import CustomPKRelatedField
from recipes.serializers.nested import (
    RecipeIngredientSerializer,
    ShortRecipeSerializer,
)
from users.serializers.nested import BaseUserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient model."""

    measurement_unit = serializers.StringRelatedField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model."""

    author = BaseUserSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(
        many=True,
        allow_empty=False,
        source='recipe_ingredients',
    )
    tags = CustomPKRelatedField(
        many=True,
        allow_empty=False,
        queryset=Tag.objects.all(),
        serializer_repr_class=TagSerializer,
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('created_at', 'updated_at')

    def get_is_favorited(self, obj):
        return getattr(obj, 'in_favorite_recipe', False)

    def get_is_in_shopping_cart(self, obj):
        return getattr(obj, 'in_shopping_cart', False)

    def validate_ingredients(self, value):
        checked_values = []
        for element in value:
            if (ingredient_obj := element['ingredient']) in checked_values:
                error_detail = {
                    'id': [f'Ingredient "{ingredient_obj.name}" is repeated.'],
                }
                raise serializers.ValidationError([error_detail])
            checked_values.append(ingredient_obj)
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')

        instance = self.Meta.model.objects.create(**validated_data)
        self._set_tags(instance, tags)
        self._set_ingredients(instance, ingredients)

        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('recipe_ingredients', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            self._set_tags(instance, tags)
        if ingredients is not None:
            self._set_ingredients(instance, ingredients)

        return instance

    def _set_tags(self, instance, tags):
        instance.tags.set(tags)

    def _set_ingredients(self, instance, ingredients):
        instance.ingredients.clear()
        IngredientsThrough = self.Meta.model.ingredients.through
        IngredientsThrough.objects.bulk_create(
            [
                IngredientsThrough(recipe=instance, **ingredient)
                for ingredient in ingredients
            ]
        )


class RecipeToUserSerializerMixin(serializers.Serializer):
    """Mixin serializer. Included `user` and `recipe` fields."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Recipe.objects.all(),
    )

    class Meta:
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return ShortRecipeSerializer().to_representation(instance.recipe)


class FavoriteRecipeSerializer(
    RecipeToUserSerializerMixin, serializers.ModelSerializer
):
    """Serializer for FavoriteRecipe model."""

    class Meta:
        model = FavoriteRecipe
        fields = RecipeToUserSerializerMixin.Meta.fields
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['user', 'recipe'],
                message='The recipe has already been added to favorites.',
            ),
        ]


class ShoppingCartSerializer(
    RecipeToUserSerializerMixin, serializers.ModelSerializer
):
    """Serializer for ShoppingCart model."""

    class Meta:
        model = ShoppingCart
        fields = RecipeToUserSerializerMixin.Meta.fields
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['user', 'recipe'],
                message=(
                    'The recipe has already been added to the shopping cart'
                ),
            ),
        ]
