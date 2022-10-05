from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers


class UserSerializer(DjoserUserSerializer):
    """Base serializer for User model."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, obj):
        try:
            return obj.is_subscribed
        except AttributeError:
            user = self.context['request'].user
            if user.is_anonymous:
                return False
            return obj.follow_to.filter(follower=user).exists()
