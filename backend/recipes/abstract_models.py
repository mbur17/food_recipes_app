from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AuthorModel(models.Model):
    """Абстрактная модель автора."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )

    class Meta:
        abstract = True


class AuthorRecipeModel(AuthorModel):
    """Абстрактная модель автора и рецепта."""
    recipe = models.ForeignKey(
        'recipes.Recipe', on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
