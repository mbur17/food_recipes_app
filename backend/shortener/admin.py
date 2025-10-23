from django.contrib import admin

from .models import UrlMap


@admin.register(UrlMap)
class UrlMapAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'short_code', 'short_url', 'full_url')
    search_fields = ('short_code', 'short_url', 'full_url', 'recipe__name')
    list_filter = ('recipe',)
    ordering = ('recipe',)
