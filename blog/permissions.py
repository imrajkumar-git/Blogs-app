from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Only the post's author (or staff) may edit/delete it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == request.user.id or request.user.is_staff
