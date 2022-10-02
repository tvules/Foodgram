from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from recipes.models import Ingredient, Recipe


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


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Short data from Recipe model."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
