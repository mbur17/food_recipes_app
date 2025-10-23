import random

from .models import UrlMap

# Убраны схожие символы: l, I, 1.
DICTIONARY = 'ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz234567890'
# Рекомендуемая длина от 2 до 10.
DEFAULT_CODE_LENGTH = 3


def generate_unique_code(length=DEFAULT_CODE_LENGTH):
    """
    Генерирует уникальный короткий код фиксированной длины.
    При коллизии повторяет попытку.
    """
    while True:
        code = ''.join(random.choice(DICTIONARY) for _ in range(length))
        if not UrlMap.objects.filter(short_code=code).exists():
            return code
