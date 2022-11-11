from .models import Channel  , StudentPickUpVerification
from accounts.serializers import (
    StudentSerializer , UserInlineSerializer , UserSerializer ,
    StudentSerializer
)
from accounts.models import Student , User  , ChannelUser       
from rest_framework import serializers




class ChannelsSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at') 
    updated_at = serializers.SerializerMethodField('get_updated_at') 
    class Meta:
        model = Channel
        fields = ['identifier','name','email','rc_number','phone_number','company_type', 'address' ,'invitation_code', 'is_active','is_verified' ,'created_at' ,  'updated_at']  

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_active':{'read_only' : True},
            'is_verified':{'read_only' : True}, 
            'invitation_code':{'read_only' : True}, 
            'created_at':{'read_only' : True}, 
            'updated_at':{'read_only' : True}, 
        }

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")
    def get_updated_at(self,obj): 
        return obj.updated_at.strftime("%m-%d-%Y")

class ChannelActivationCodeConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=False) 
    code = serializers.CharField(allow_blank=False) 


class ChannelUserSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at') 
    updated_at = serializers.SerializerMethodField('get_updated_at') 
    class Meta:  
        model = ChannelUser
        fields = ['identifier', 'channel','is_admin', 'is_staff' , 'created_at' , 'updated_at' ]

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_active':{'read_only' : True},
            'created_at':{'read_only' : True}, 
            'updated_at':{'read_only' : True}, 
        }

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")

    def get_updated_at(self,obj): 
        return obj.updated_at.strftime("%m-%d-%Y")

    
    


class ChannelUserFullDetailSerializer(serializers.ModelSerializer):
    user = UserInlineSerializer(read_only=True)
    children = serializers.SerializerMethodField('get_children')
    created_at = serializers.SerializerMethodField('get_created_at') 
    updated_at = serializers.SerializerMethodField('get_updated_at') 
    class Meta:  
        model = ChannelUser
        fields = ['identifier', 'user' , 'channel','is_admin', 'is_staff' ,'children' , 'created_at' , 'updated_at' ]

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_active':{'read_only' : True},
            'created_at':{'read_only' : True}, 
            'updated_at':{'read_only' : True}, 
        }

    def get_children(self, obj):
        students = Student.objects.filter(channel__id=obj.channel.id , parent__id=obj.id)
        serializer = StudentSerializer(students , many=True)
        return serializer.data


    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")
    def get_updated_at(self,obj): 
        return obj.updated_at.strftime("%m-%d-%Y")



class ChannelJoinSerializer(serializers.Serializer):
    invitation_code = serializers.CharField(allow_blank=False) 




class StudentPickUpVerificationHistorySerializer(serializers.ModelSerializer):
    # student = StudentSerializer(read_only=True)
    class Meta:
        model = StudentPickUpVerification
        fields = ['date' ,'completed', 'created_at' , 'updated_at'] 
        # fields = [ 'student' , 'date' , 'created_at' , 'updated_at']



class ChannelUserUploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()