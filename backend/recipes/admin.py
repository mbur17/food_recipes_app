from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


class IngredientInRecipeInline(admin.TabularInline):
    """Инлайн для редактирования ингредиентов в рецептах."""
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = (IngredientInRecipeInline,)
    readonly_fields = ('favorites_count',)

    def get_queryset(self, request):
        """
        Оптимизация запросов с предварительным подсчётом кол-ва избранных.
        """
        queryset = super().get_queryset(request)
        return queryset.annotate(favorites_count=Count('favorites'))

    def favorites_count(self, obj):
        """Общее число добавлений рецепта в избранное."""
        return obj.favorites_count

    favorites_count.short_description = 'В избранном'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe')
    search_fields = ('author__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe')
    search_fields = ('author__username', 'recipe__name')
