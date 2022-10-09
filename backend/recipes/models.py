from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .fields import HEXColorField
from .managers import RecipeManager
from users.models import BaseModel

User = get_user_model()


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(unique=True, db_index=True, max_length=200)
    color = HEXColorField(unique=True)
    slug = models.SlugField(unique=True, max_length=200)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class MeasurementUnit(models.Model):
    """Measurement unit model."""

    name = models.CharField(unique=True, max_length=30)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(db_index=True, max_length=200)
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return self.name


class Recipe(BaseModel):
    """Recipe model."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        db_index=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
    )
    name = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
    )

    objects = RecipeManager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def _get_old_image(self):
        if self.pk is None:
            return None
        try:
            return self.__class__.objects.get(pk=self.pk).image
        except self.__class__.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        old_image = self._get_old_image()
        save_result = super().save(*args, **kwargs)
        if old_image is not None and old_image != self.image:
            old_image.delete(save=False)
        return save_result

    def delete(self, *args, **kwargs):
        delete_result = super().delete(*args, **kwargs)
        self.image.delete(save=False)
        return delete_result


class RecipeTag(models.Model):
    """Model for m2m: Recipe-Tags."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tags',
        db_index=True,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'recipes_recipe_tags'
        verbose_name = 'tag'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag',
            ),
        ]


class RecipeIngredient(models.Model):
    """Model for m2m: Recipe-Ingredients."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        db_index=True,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
    )

    class Meta:
        db_table = 'recipes_recipe_ingredients'
        verbose_name = 'ingredient'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        ]


class BaseRecipeToUser(BaseModel):
    """Base model to `recipe-user`. Included `user` and `recipe` fields."""

    updated_at = None
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='in_%(class)s',
        db_index=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_%(class)s',
    )

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class FavoriteRecipe(BaseRecipeToUser):
    """Favorite recipe model."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe',
            ),
        ]


class ShoppingCart(BaseRecipeToUser):
    """Shopping cart model."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart_recipe',
            ),
        ]
