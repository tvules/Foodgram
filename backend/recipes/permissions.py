from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAuthor(permissions.BasePermission):
    """Only author have access for update/delete."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
