from django.db.models import Sum

from recipes.models import IngredientInRecipe


def generate_shopping_list(user):
    """Генерирует содержимое файла со списком покупок текущего пользователя."""
    shopping_cart = (
        IngredientInRecipe.objects
        .filter(recipe__shopping_cart__author=user)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(total_amount=Sum('amount'))
    )
    if not shopping_cart.exists():
        return None
    shopping_list = 'Список покупок:\n\n'
    for item in shopping_cart:
        shopping_list += (
            f'- {item["ingredient__name"]} '
            f'({item["total_amount"]} '
            f'{item["ingredient__measurement_unit"]})\n'
        )
    return shopping_list
