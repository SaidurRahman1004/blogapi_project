from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Only author can edit/delete their posts
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for author
        return obj.author == request.user
