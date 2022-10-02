from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import exceptions, generics, mixins, permissions
from rest_framework.settings import api_settings

from .models import Follow
from .paginations import PageNumberLimitPagination
from .serializers import FollowSerializer, FollowToSerializer
from .services import clean_recipe_limit_param

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Djoser view set for User model."""

    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.is_subscribed(self.request.user)


class FollowToListView(generics.ListAPIView):
    """Returns a list of users the author is follow to."""

    serializer_class = FollowToSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PageNumberLimitPagination

    def get(self, request, *args, **kwargs):
        clean_recipe_limit_param(request)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            User.objects.prefetch_related('recipes')
            .filter(follow_to__follower_id=self.request.user.id)
            .order_by('-follow_to__created_at')
        )


class FollowView(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView
):
    """Create/destroy view for Follow model."""

    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'follow_to_id'
    error_messages = {'not_follower': 'You are not a follower.'}

    def post(self, request, *args, **kwargs):
        clean_recipe_limit_param(request)
        request.data['follow_to'] = kwargs['follow_to_id']
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        return Follow.objects.filter(follower_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        follow_to = get_object_or_404(
            User.objects.prefetch_related('recipes'),
            pk=kwargs['follow_to_id'],
        )
        response = super().create(request, *args, **kwargs)
        repr_serializer = FollowToSerializer(
            follow_to, context=self.get_serializer_context()
        )
        response.data = repr_serializer.data
        return response

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Http404 as exc:
            pk = kwargs['follow_to_id']
            if User.objects.filter(pk=pk).exists():
                raise exceptions.ValidationError(
                    {
                        api_settings.NON_FIELD_ERRORS_KEY: [
                            self.error_messages['not_follower']
                        ]
                    }
                )
            raise exc
