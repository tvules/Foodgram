from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import Follow

User = get_user_model()


class BaseUserSerializer(UserSerializer):
    """Base serializer for User model."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.follow_to.filter(follower=request.user).exists()


class FollowToSerializer(BaseUserSerializer):
    """Serializer for User model on follow page."""

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow model."""

    follower = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Follow
        fields = ('follower', 'follow_to')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['follower', 'follow_to'],
            )
        ]

    def validate(self, attrs):
        if attrs['follow_to'] == attrs['follower']:
            raise serializers.ValidationError(
                'You cannot follow to yourself.',
            )
        return attrs
