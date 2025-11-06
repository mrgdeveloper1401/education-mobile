from rest_framework import permissions


class AsyncRemoveAuthenticationPermissions:

    async def has_permission(self, request, view):
        user = await request.auser()
        if user.is_authenticated:
            return False
        return True
