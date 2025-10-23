from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

AVATAR_DIR = 'users/'
NAME_MAX_LENGTH = 150


class FoodgramUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=NAME_MAX_LENGTH)
    avatar = models.ImageField('Аватар', upload_to=AVATAR_DIR, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} ({self.email})'


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        unique_together = ('user', 'author')
        ordering = ('user',)
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'

    def clean(self):
        """Запрещает подписку на самого себя."""
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
