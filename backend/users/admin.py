from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm
from .models import Follow, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'username',
                    'password1',
                    'password2',
                ),
            },
        ),
    )


@admin.register(Follow)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('follower', 'follow_to', 'created_at')
    search_fields = ('follower__email',)
