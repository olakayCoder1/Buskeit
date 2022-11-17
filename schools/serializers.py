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
            'email':{'read_only' : True}, 
            'company_type':{'read_only' : True}, 
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
    students = serializers.SerializerMethodField('get_students') 
    class Meta:  
        model = ChannelUser
        fields = ['identifier','first_name', 'last_name','email' , 'channel','is_parent','is_admin', 'is_staff' , 'created_at' , 'updated_at', 'students' ]

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_active':{'read_only' : True},
            'channel':{'read_only' : True}, 
            'is_parent':{'read_only' : True}, 
            'is_admin':{'read_only' : True}, 
            'is_staff':{'read_only' : True}, 
            'created_at':{'read_only' : True}, 
            'updated_at':{'read_only' : True}, 
        }

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")

    def get_updated_at(self,obj): 
        return obj.updated_at.strftime("%m-%d-%Y")  
   

    def get_students(self, obj):
        kids = Student.objects.filter(parent__identifier=obj.identifier , channel__identifier=obj.channel.identifier)
        return StudentSerializer(kids , many=True).data

    
    
class MapStudentsToParentSerializer(serializers.Serializer):    
    students = serializers.ListField()
    def validate(self, attrs):
        if len(attrs['students']) == 0:
            raise serializers.ValidationError({'student':'Students list cannot be empty'})
        return super().validate(attrs)

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