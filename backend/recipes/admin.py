from django.contrib import admin
from django.db.models import Count

from .models import (
    FavoriteRecipe,
    Ingredient,
    MeasurementUnit,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('^name', '^slug')
    list_display_links = ('name',)


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('^name',)
    list_display_links = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('^name',)
    list_display_links = ('name',)


class TagsInline(admin.TabularInline):
    model = RecipeTag
    min_num = 1
    extra = 0


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_select_related = True
    inlines = (TagsInline, IngredientInline)
    list_display = ('id', 'name', 'author', 'in_favorites')
    list_display_links = ('name',)
    search_fields = (
        'name',
        '^author__username',
        '^author__first_name',
        '^author__last_name',
        '^author__email',
    )
    list_filter = ('tags',)

    @admin.display()
    def in_favorites(self, obj):
        return obj.in_favorites

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(in_favorites=Count('in_favoriterecipe'))


@admin.register(FavoriteRecipe, ShoppingCart)
class BaseRecipeToUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')
    search_fields = (
        'recipe__name',
        '^user__username',
        '^user__first_name',
        '^user__last_name',
        '^user__email',
    )
    list_display_links = ('recipe',)
