from rest_framework import permissions


class IsAccountVerified(permissions.DjangoModelPermissions):

    def has_permission(self, request, view):
        return request.user.is_verified
     
    