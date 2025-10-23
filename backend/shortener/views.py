from django.shortcuts import get_object_or_404, redirect

from .models import UrlMap


def redirect_to_full_url(request, short_code):
    """Редирект пользователя на полный URL по короткому коду."""
    url_map = get_object_or_404(UrlMap, short_code=short_code)
    return redirect(url_map.full_url)
