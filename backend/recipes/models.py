from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .abstract_models import AuthorModel, AuthorRecipeModel
from .constants import (COOKING_MAX_TIME, COOKING_MIN_TIME,
                        INGREDIENT_MAX_AMOUNT, INGREDIENT_MAX_LENGTH,
                        INGREDIENT_MIN_AMOUNT, RECIPE_IMAGE_DIR,
                        RECIPE_MAX_LENGTH, TAG_MAX_LENGTH, UNIT_MAX_LENGTH)

User = get_user_model()


class Tag(models.Model):

    name = models.CharField('Название', max_length=TAG_MAX_LENGTH, unique=True)
    slug = models.SlugField('Слаг', max_length=TAG_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        'Название', max_length=INGREDIENT_MAX_LENGTH, db_index=True
    )
    measurement_unit = models.CharField(
        'Единицы измерения', max_length=UNIT_MAX_LENGTH
    )

    class Meta:
        unique_together = ('name', 'measurement_unit')
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(AuthorModel):

    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты', through='IngredientInRecipe'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    image = models.ImageField('Картинка', upload_to=RECIPE_IMAGE_DIR)
    name = models.CharField('Название', max_length=RECIPE_MAX_LENGTH)
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                COOKING_MIN_TIME,
                f'Значение не должно быть меньше {COOKING_MIN_TIME}.',
            ),
            MaxValueValidator(
                COOKING_MAX_TIME,
                'Значение должно быть реалистичным.',
            ),
        ]
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                INGREDIENT_MIN_AMOUNT,
                f'Значение не должно быть меньше {INGREDIENT_MIN_AMOUNT}.',
            ),
            MaxValueValidator(
                INGREDIENT_MAX_AMOUNT,
                f'Значение не должно быть больше {INGREDIENT_MAX_AMOUNT}.',
            ),
        ],
    )

    class Meta:
        unique_together = ('ingredient', 'recipe')
        ordering = ('ingredient__name',)
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class Favorite(AuthorRecipeModel):

    class Meta:
        unique_together = ('author', 'recipe')
        ordering = ('author',)
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.author.username}'


class ShoppingCart(AuthorRecipeModel):

    class Meta:
        unique_together = ('author', 'recipe')
        ordering = ('author',)
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe.name} в корзине у {self.author.username}'
