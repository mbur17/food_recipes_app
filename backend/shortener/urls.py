from django.urls import path

from .views import redirect_to_full_url

app_name = 'shortener'

urlpatterns = [
    path('s/<str:short_code>/', redirect_to_full_url, name='redirect'),
]
