from rest_framework import permissions
from accounts.models import ChannelUser

class IsStudentParent(permissions.DjangoModelPermissions):
     
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.parent.user.id 


class IsStudentParentOrChannelStaff(permissions.DjangoModelPermissions):
     
    def has_object_permission(self, request, view, obj):
        if ChannelUser.objects.filter(channel__id=obj.channel.id , user__id=request.user.id , is_staff=True):
            return True
        if request.user.id == obj.parent.user.id :
            return True
        return False





