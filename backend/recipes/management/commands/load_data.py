import json
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

CONTAINER_FILE_PATH = '/app/ingredients.json'


class Command(BaseCommand):
    help = 'Загружает ингредиенты в базу данных из ingredients.json'

    def handle(self, *args, **kwargs):
        file_path = CONTAINER_FILE_PATH
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'Файл {file_path} не найден!'))
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for item in data:
                    Ingredient.objects.get_or_create(
                        name=item['name'],
                        measurement_unit=item['measurement_unit']
                    )
            self.stdout.write(
                self.style.SUCCESS('Ингредиенты успешно загружены!')
            )
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR('Ошибка: Некорректный JSON-файл!')
            )
