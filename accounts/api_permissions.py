"""
Shared object-level permission helpers used by the blog & reviews apps.
Kept in accounts/ so both apps can import from one place without a
circular-dependency risk.
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrAdminOrReadOnly(BasePermission):
    """
    Anyone can read (GET/HEAD/OPTIONS). Only the object's owner
    (checked via obj.author or obj.user) or an admin (is_staff) may
    write/delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        owner_id = getattr(obj, "author_id", None) or getattr(obj, "user_id", None)
        return owner_id == request.user.id or request.user.is_staff


class IsVerifiedUser(BasePermission):
    """
    Requires the logged-in user to have completed OTP email verification
    before they can create content (posts, comments, reviews).
    Read-only (GET) requests are always allowed.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )
