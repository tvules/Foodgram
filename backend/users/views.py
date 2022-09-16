from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import exceptions, generics, permissions, status
from rest_framework.response import Response
from rest_framework.settings import api_settings

from .paginations import PageNumberLimitPagination
from .serializers import FollowSerializer, FollowToSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Djoser view set for User model."""

    pagination_class = PageNumberLimitPagination


class FollowToListView(generics.ListAPIView):
    """Returns a list of users the author is follow to."""

    serializer_class = FollowToSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        return User.objects.filter(follow_to__follower=self.request.user)


class FollowView(generics.CreateAPIView, generics.DestroyAPIView):
    """Create/destroy view for Follow model."""

    serializer_class = FollowSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        follow_to = self.get_object()

        serializer = self.get_serializer(data={'follow_to': follow_to.pk})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        follow_to_serializer = self._get_follow_to_serializer(follow_to)
        headers = self.get_success_headers(serializer.data)
        return Response(
            follow_to_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def _get_follow_to_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        return FollowToSerializer(*args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        follow_to = self.get_object()

        instance = self.request.user.follower.filter(follow_to=follow_to)
        if not instance:
            raise exceptions.ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: ['You are not a follower']}
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
