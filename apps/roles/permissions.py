from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allow access only to users with the 'admin' role."""
    message = 'You must have the admin role to perform this action.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_role('admin')
        )


class IsEditorRole(BasePermission):
    """Allow access to users with 'admin' or 'editor' roles."""
    message = 'You must have the editor role to perform this action.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.has_role('admin') or request.user.has_role('editor'))
        )


class HasPermission(BasePermission):
    """
    Dynamic permission check based on a required_permission attribute on the view.

    Usage on a view:
        required_permission = 'user:delete'
    """
    message = 'You do not have the required permission.'

    def has_permission(self, request, view):
        required = getattr(view, 'required_permission', None)
        if not required:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_permission_code(required)
        )


def require_permission(codename):
    """
    Factory that creates a permission class checking for a specific codename.

    Usage:
        permission_classes = [require_permission('report:view')]
    """
    class DynamicPermission(BasePermission):
        message = f"You need the '{codename}' permission to do this."

        def has_permission(self, request, view):
            return bool(
                request.user and
                request.user.is_authenticated and
                request.user.has_permission_code(codename)
            )

    DynamicPermission.__name__ = f'Has_{codename}_Permission'
    return DynamicPermission
