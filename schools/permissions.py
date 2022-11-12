from rest_framework import permissions
from accounts.models import ChannelUser

class IsStudentParent(permissions.DjangoModelPermissions):
     
    def has_object_permission(self, request, view, obj):
        if obj.parent == None :
            return False
        return bool(request.user and request.user.is_authenticated  and request.user == obj.parent.user)
  


class IsChannelAdmin(permissions.DjangoModelPermissions):
     
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and obj.__class__.objects.filter(user__id=request.user.id, is_admin=True).exist()) 


class IsStudentParentOrChannelStaff(permissions.DjangoModelPermissions): 
     
    def has_object_permission(self, request, view, obj):
        if ChannelUser.objects.filter(channel__id=obj.channel.id , user__id=request.user.id , is_staff=True):
            return True
        if request.user.id == obj.parent.user.id :
            return True
        return False





