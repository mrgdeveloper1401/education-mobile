from rest_framework import permissions

from apis.utils.custom_exceptions import AuthenticationFailed


class AsyncRemoveAuthenticationPermissions(permissions.BasePermission):
    async def has_permission(self, request, view):
        if request.user.is_authenticated:
            raise AuthenticationFailed()
        return True


class AsyncIsAuthenticated(permissions.BasePermission):
    async def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if obj.user_id == request.user.id:
            return True
        else:
            if request.method in permissions.SAFE_METHODS:
                return True
            else:
                return False
