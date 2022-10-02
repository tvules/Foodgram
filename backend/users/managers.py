from django.apps import apps
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models import Exists, OuterRef, Value

app_config = apps.get_app_config('users')


class UserQuerySet(models.QuerySet):
    def is_subscribed(self, user):
        """
        Return a queryset in which the returned objects have been annotated
        with `is_subscribed` field.
        """
        if user.is_anonymous:
            return self.annotate(is_subscribed=Value(False))

        return self.annotate(
            is_subscribed=Exists(
                app_config.get_model('Follow').objects.filter(
                    follower_id=user.id, follow_to_id=OuterRef('pk')
                ),
            ),
        )


class UserManager(DjangoUserManager.from_queryset(UserQuerySet)):
    pass
