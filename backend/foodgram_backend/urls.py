from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.users.urls', namespace='users')),
    path('api/', include('api.recipes.urls', namespace='recipes')),
    path('', include('shortener.urls', namespace='shortener'))
]
