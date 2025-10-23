from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from shortener.models import UrlMap
from shortener.services import generate_unique_code

from ..filters import IngredientFilterSet, RecipeFilterSet
from ..pagination import FoodgramPagination
from ..permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)
from .services import generate_shopping_list


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilterSet


class RecipeViewSet(ModelViewSet):
    pagination_class = FoodgramPagination
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects
        if self.action == 'favorites':
            queryset = queryset.filter(favorited_by__author=user)
        elif self.action == 'shopping_cart':
            queryset = queryset.filter(shopping_cart__author=user)
        return queryset.prefetch_related(
            'tags', 'recipe_ingredients__ingredient', 'author'
        ).order_by('-created_at').all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        elif self.action == 'favorite':
            return FavoriteSerializer
        elif self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return CreateRecipeSerializer

    def _post_relationship(self, model, serializer_class, user, recipe):
        """Общая логика добавления в избранное или список покупок."""
        serializer = serializer_class(
            data={'recipe': recipe.id}, context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete_relationship(self, model, user, recipe):
        """Общая логика удаления из избранного или списка покупок."""
        item = model.objects.filter(author=user, recipe=recipe).first()
        if item:
            item.delete()
            return Response(
                {'detail': f'Рецепт удалён из {model._meta.verbose_name}.'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'detail': f'Рецепт отсутствует в {model._meta.verbose_name}.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        domain = request.get_host()
        scheme = request.scheme
        short_code = generate_unique_code()
        url_map, created = UrlMap.objects.get_or_create(
            recipe=recipe,
            defaults={
                'full_url': f'{scheme}://{domain}/recipes/{recipe.id}/',
                'short_code': short_code,
                'short_url': f'/s/{short_code}'
            }
        )
        return Response(
            {'short-link': f'{scheme}://{domain}{url_map.short_url}'}
        )

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        user = request.user
        shopping_list = generate_shopping_list(user)
        if not shopping_list:
            return Response(
                'Список покупок пуст.',
                content_type='text/plain',
                status=status.HTTP_204_NO_CONTENT
            )
        response = Response(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(detail=True, methods=['post'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._post_relationship(
            ShoppingCart, ShoppingCartSerializer, request.user, recipe
        )

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._delete_relationship(ShoppingCart, request.user, recipe)

    @action(detail=True, methods=['post'], url_path='favorite')
    def favorites(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._post_relationship(
            Favorite, FavoriteSerializer, request.user, recipe
        )

    @favorites.mapping.delete
    def remove_from_favorites(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._delete_relationship(Favorite, request.user, recipe)
