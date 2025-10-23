from django.contrib import admin

from .models import FoodgramUser, Subscription


@admin.register(FoodgramUser)
class FoodgramUserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff', 'avatar'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = (
        'user__email',
        'user__username',
        'author__email'
        'author__username',
    )
