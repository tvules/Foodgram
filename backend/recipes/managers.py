from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Exists, OuterRef, Prefetch

from users.models import Follow

User = get_user_model()
app_config = apps.get_app_config('recipes')


class RecipeManager(models.Manager):
    def setup_eager_loading(self, user):
        RecipeIngredient = app_config.get_model('RecipeIngredient')
        FavoriteRecipe = app_config.get_model('FavoriteRecipe')
        ShoppingCart = app_config.get_model('ShoppingCart')

        author_qs = User.objects.annotate(
            is_subscribed=Exists(
                Follow.objects.filter(
                    follower_id=user.id, follow_to_id=OuterRef('pk')
                ),
            ),
        )
        ingredients_qs = RecipeIngredient.objects.select_related(
            'ingredient__measurement_unit'
        )

        queryset = self.prefetch_related(
            'tags',
            Prefetch('author', queryset=author_qs),
            Prefetch('recipe_ingredients', queryset=ingredients_qs),
        ).annotate(
            in_favorite_recipe=Exists(
                FavoriteRecipe.objects.filter(
                    recipe_id=OuterRef('pk'), user_id=user.id
                ),
            ),
            in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    recipe_id=OuterRef('pk'), user_id=user.id
                ),
            ),
        )
        return queryset
