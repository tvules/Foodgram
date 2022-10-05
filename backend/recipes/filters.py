from django_filters import rest_framework as filters

from recipes.models import Tag, User


class IngredientFilter(filters.FilterSet):
    """FilterSet for IngredientViewSet."""

    name = filters.CharFilter(lookup_expr='istartswith')


class RecipeFilter(filters.FilterSet):
    """FilterSet for RecipeViewSet."""

    author = filters.ModelChoiceFilter(
        field_name='author_id',
        queryset=User.objects.all(),
    )
    tags = filters.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(method='shoppingcart_filter')

    def shoppingcart_filter(self, queryset, name, value):
        user = self.request.user
        if value is True and user.is_authenticated:
            return queryset.filter(in_shoppingcart__user_id=user.id)
        return queryset

    def favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value is True and user.is_authenticated:
            return queryset.filter(in_favoriterecipe__user_id=user.id)
        return queryset
