from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, FollowToListView, FollowView

app_name = 'users'

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='user')

urlpatterns = [
    path(
        'users/subscriptions/', FollowToListView.as_view(), name='follow-list'
    ),
    path('users/<int:pk>/subscribe/', FollowView.as_view(), name='follow'),
]

urlpatterns += router.urls
