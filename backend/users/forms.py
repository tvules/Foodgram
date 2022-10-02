from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm as DjangoUserCreationForm,
)

User = get_user_model()


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name')
