from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, generics, mixins, permissions
from rest_framework.settings import api_settings

from recipes.models import Recipe


class BaseRecipeToUserView(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView
):
    """Base view for "recipe + user" model"""

    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'recipe_id'
    error_messages = {'not_in': 'The recipe does not exist in your {0}.'}
    list_name = None

    def post(self, request, *args, **kwargs):
        request.data['recipe'] = kwargs['recipe_id']
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        get_object_or_404(Recipe, pk=kwargs['recipe_id'])
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user_id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Http404 as exc:
            pk = kwargs['recipe_id']
            if Recipe.objects.filter(pk=pk).exists():
                message = self.error_messages['not_in']
                raise exceptions.ValidationError(
                    {
                        api_settings.NON_FIELD_ERRORS_KEY: [
                            message.format(self.get_list_name())
                        ]
                    }
                )
            raise exc

    def get_list_name(self):
        assert self.list_name is not None, (
            "'%s' should either include a `list_name` attribute, "
            "or override the `get_list_name()` method."
            % self.__class__.__name__
        )
        return self.list_name
