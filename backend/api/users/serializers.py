from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import Subscription

from ..fields import Base64ImageField

User = get_user_model()


class FoodgramUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name'
        )


class FoodgramUserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):

        """Проверяет подписку текущего пользователя."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.subscribers.filter(user=user).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserRecipeSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True, source='recipes.count'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_recipes(self, obj):
        from api.recipes.serializers import ShortRecipeSerializer
        request = self.context['request']
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        # Проверяем recipes_limit перед преобразованием в int,
        # чтобы избежать ошибок.
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('author', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'user'),
                message='Вы уже подписаны на этого пользователя.',
            )
        ]

    def validate_author(self, author):
        """Запрещает подписываться на самого себя."""
        if self.context['request'].user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        return author

    def to_representation(self, instance):
        return UserRecipeSerializer(instance.author, context=self.context).data
