from .models import School , Channel 
from accounts.serializers import (
    StudentSerializer , UserInlineSerializer , UserSerializer ,
    ParentInlineSerializer , StudentSerializer
)
from accounts.models import Parent, Student , User  , ChannelUser      
from rest_framework import serializers




class ChannelsSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at') 
    updated_at = serializers.SerializerMethodField('get_updated_at') 
    class Meta:
        model = Channel
        fields = ['identifier','name','email','rc_number','phone_number', 'address' , 'is_active','is_verified' ,'created_at' ,  'updated_at']  

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_active':{'read_only' : True},
            'is_verified':{'read_only' : True}, 
            'created_at':{'read_only' : True}, 
            'updated_at':{'read_only' : True}, 
        }

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")
    def get_updated_at(self,obj): 
        return obj.updated_at.strftime("%m-%d-%Y")


class ChannelUserSerializer(serializers.ModelSerializer):
    user = UserInlineSerializer(read_only=True)
    created_at = serializers.SerializerMethodField('get_created_at') 
    updated_at = serializers.SerializerMethodField('get_updated_at') 
    class Meta:  
        model = ChannelUser
        fields = ['identifier', 'user' , 'channel','is_admin', 'is_staff' , 'created_at' , 'updated_at' ]

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_active':{'read_only' : True},
            'created_at':{'read_only' : True}, 
            'updated_at':{'read_only' : True}, 
        }

    
    


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

class SchoolSerializer(serializers.ModelSerializer):
    # students = serializers.SerializerMethodField('school_students')
    # parents = serializers.SerializerMethodField('school_parents') 
    created_at = serializers.SerializerMethodField('get_created_at') 
    class Meta:
        model = School
        fields = ['identifier','name', 'address' , 'is_active','is_verified' ,'created_at']  
        # fields = ['identifier','name', 'address' , 'is_active','is_verified' ,'created_at','students', 'parents'] 


        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_active':{'read_only' : True},
            'is_verified':{'read_only' : True}, 
        }

    def school_students(self , obj):
        users =Student.objects.filter(school__identifier=obj.identifier)
        return StudentSerializer(users, many=True).data
 
    def school_parents(self , obj):
        users =Parent.objects.filter(school__identifier=obj.identifier)
        return ParentInlineSerializer(users, many=True).data



    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")
        