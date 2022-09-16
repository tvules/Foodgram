from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """The "created_at" and "updated_at" fields are included."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    """User model."""

    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta(AbstractUser.Meta):
        db_table = 'auth_user'


class Follow(BaseModel):
    """Follow model."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='follower',
    )
    follow_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follow_to',
        verbose_name='follow to',
    )
    updated_at = None

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'follow_to'],
                name='unique_follow',
            ),
        ]

    def clean(self):
        if self.follower == self.follow_to:
            raise ValidationError(
                {'follow_to': 'You cannot follow to yourself.'}
            )
