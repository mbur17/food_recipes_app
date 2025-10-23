from rest_framework import serializers

from api.users.serializers import FoodgramUserSerializer
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)

from ..fields import Base64ImageField

AMOUNT_AND_TIME_MAX_VALUE = 32_000
AMOUNT_AND_TIME_MIN_VALUE = 1


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор представления ингредиента в рецепте."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ShortIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор короткого представления ингредиента."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    amount = serializers.IntegerField(
        max_value=AMOUNT_AND_TIME_MAX_VALUE,
        min_value=AMOUNT_AND_TIME_MIN_VALUE
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """Проверяет рецепт в избранном текущего пользователя."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверяет рецепт в корзине текущего пользователя."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.shopping_cart.filter(recipe=obj).exists()
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = ShortIngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        max_value=AMOUNT_AND_TIME_MAX_VALUE,
        min_value=AMOUNT_AND_TIME_MIN_VALUE
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate_ingredients(self, ingredients):
        """Проверка ингредиентов."""
        if not ingredients:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один ингредиент.'
            )
        unique_ingredients = set()
        for item in ingredients:
            ingredient_id = item['ingredient'].id
            if ingredient_id in unique_ingredients:
                raise serializers.ValidationError(
                    f'Ингредиент с id={ingredient_id} дублируется.'
                )
            unique_ingredients.add(ingredient_id)
        return ingredients

    def validate_tags(self, tags):
        """Проверка тегов."""
        if not tags:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один тег.'
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return tags

    def validate_image(self, image_data):
        if image_data is None:
            raise serializers.ValidationError(
                'Изображение для рецепта обязательно.'
            )
        return image_data

    def _save_tags(self, instance, tags_data):
        """Обработка тегов для рецепта."""
        instance.tags.set(tags_data)

    def _save_ingredients(self, instance, ingredients_data):
        """Обработка ингредиентов для рецепта."""
        instance.recipe_ingredients.all().delete()
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ])

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        self._save_tags(recipe, tags_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError({
                'ingredients': (
                    'Поле "ingredients" обязательно для обновления рецепта.'
                )
            })
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                {'tags': 'Поле "tags" обязательно для обновления рецепта.'}
            )
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        self._save_tags(instance, tags_data)
        self._save_ingredients(instance, ingredients_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Возвращает созданный рецепт в нужном формате."""
        return RecipeSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор короткого представления рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AuthorRecipeSerializer(serializers.ModelSerializer):
    """Абстрактный сериализатор автора и рецепта."""

    _recipe_added_to: str = None

    class Meta:
        model = None
        fields = ('author', 'recipe')
        read_only_fields = ('author',)

    def validate(self, attrs):
        recipe = attrs['recipe']
        user = self.context['request'].user
        if self.Meta.model.objects.filter(author=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт уже добавлен в {self._recipe_added_to}.'
            )
        return attrs

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(AuthorRecipeSerializer):
    _recipe_added_to = 'избранное'

    class Meta(AuthorRecipeSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(AuthorRecipeSerializer):
    _recipe_added_to = 'список покупок'

    class Meta(AuthorRecipeSerializer.Meta):
        model = ShoppingCart
