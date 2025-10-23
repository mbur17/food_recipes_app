from django.contrib.auth import get_user_model
from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter)

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilterSet(FilterSet):
    """Фильтр сет ингрединетов."""
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilterSet(FilterSet):
    """Фильтр сет рецептов."""
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = BooleanFilter(method='is_favorite_filter')
    is_in_shopping_cart = BooleanFilter(method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def _filter_by_related_name(self, queryset, related_name, user, value):
        """Общая логика фильтрации по связанным объектам."""
        if not user.is_authenticated:
            return queryset.none()
        if value:
            return queryset.filter(**{f'{related_name}__author': user})
        return queryset.exclude(**{f'{related_name}__author': user})

    def is_favorite_filter(self, queryset, name, value):
        """
        Фильтрация рецептов, добавленных в избранное текущего пользователя.
        """
        return self._filter_by_related_name(
            queryset, 'favorites', self.request.user, value
        )

    def is_in_shopping_cart_filter(self, queryset, name, value):
        """Фильтрация рецептов, находящихся в корзине текущего пользователя."""
        return self._filter_by_related_name(
            queryset, 'shopping_cart', self.request.user, value
        )
