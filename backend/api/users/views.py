from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..pagination import FoodgramPagination
from .serializers import AvatarSerializer, SubscriptionSerializer

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):

    pagination_class = FoodgramPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return super().get_queryset().prefetch_related(
                models.Prefetch(
                    'subscribers',
                    queryset=user.subscribers.all()
                )
            )
        return User.objects.all()

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Добавление или удаление аватара текущего пользователя."""
        user = request.user
        serializer = AvatarSerializer(data=request.data, instance=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        avatar_url = (request.build_absolute_uri(user.avatar.url))
        return Response({'avatar': avatar_url}, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete(save=True)
        return Response(
            {'avatar': None}, status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def list_subscriptions(self, request):
        """Список подписок текущего пользователя."""
        subscriptions = request.user.subscriptions.select_related('author')
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            subscriptions, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = SubscriptionSerializer(
            data={'author': author.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        subscription = request.user.subscriptions.select_related(
            'author'
        ).filter(author=author).first()
        if not subscription:
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
