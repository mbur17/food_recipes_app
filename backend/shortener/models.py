from django.db import models

from recipes.models import Recipe

SHORT_CODE_MAX_LENGTH = 10
SHORT_URL_MAX_LENGTH = 254


class UrlMap(models.Model):
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE)
    full_url = models.TextField()
    short_code = models.CharField(
        max_length=SHORT_CODE_MAX_LENGTH, unique=True
    )
    short_url = models.CharField(
        max_length=SHORT_URL_MAX_LENGTH, unique=True, db_index=True
    )

    class Meta:
        ordering = ('recipe__created_at',)
        verbose_name = 'Короткую ссылку'
        verbose_name_plural = 'Короткие ссылки'

    def __str__(self):
        return '{} - {}'.format(self.recipe, self.short_url)
