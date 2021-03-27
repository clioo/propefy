from rest_framework.permissions import BasePermission


class UserHasBusiness(BasePermission):
    """Permission to check if user has a business assigned."""
    message = 'There is no business assigned to this user.'

    def has_permission(self, request, view):
        return bool(request.user and (request.user.business is not None))
