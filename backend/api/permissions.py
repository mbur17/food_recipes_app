from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """Доступ автору или только для чтения."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
