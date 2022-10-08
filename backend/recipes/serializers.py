from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
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
from users.serializers.nested import UserSerializer

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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ingredient serializer for Recipe model."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(32767)],
    )

    class Meta:
        model = Recipe.ingredients.through
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model."""

    author = UserSerializer(default=serializers.CurrentUserDefault())
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
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(32767)],
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

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

        if tags:
            self._set_tags(instance, tags)
        if ingredients:
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
        queryset=Recipe.objects.all(),
    )

    class Meta:
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        fields = ('id', 'name', 'image', 'cooking_time')
        return RecipeSerializer(instance.recipe, fields=fields).data


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
                    'The recipe has already been added to the shopping cart.'
                ),
            ),
        ]
