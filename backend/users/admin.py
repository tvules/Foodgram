from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .forms import UserCreationForm
from .models import Follow, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
    )
    list_display_links = ('username',)
    add_form = UserCreationForm
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
