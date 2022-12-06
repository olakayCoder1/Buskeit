from .models import User , Student , ChannelUser
from rest_framework import serializers
from schools.models import Channel
# from schools.serializers import *
from django.conf import settings



class StudentSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at')
    class Meta:
        model = Student
        fields =['identifier', 'first_name' , 'last_name', 'created_at']

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y") 


class ChannelsInSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at') 
    updated_at = serializers.SerializerMethodField('get_updated_at') 
    class Meta:
        model = Channel
        fields = ['identifier','name','email', 'phone_number', 'address' ,'invitation_code' ,'created_at' ,  'updated_at']  

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_verified':{'read_only' : True}, 
            'invitation_code':{'read_only' : True}, 
            'created_at':{'read_only' : True}, 
            'updated_at':{'read_only' : True}, 
        }

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")
    def get_updated_at(self,obj): 
        return obj.updated_at.strftime("%m-%d-%Y")



class ChannelUserSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at') 
    updated_at = serializers.SerializerMethodField('get_updated_at') 
    students = serializers.SerializerMethodField('get_students') 
    channel = ChannelsInSerializer(read_only=True)

    class Meta:  
        model = ChannelUser
        fields = ['identifier', 'channel','is_admin', 'is_staff' , 'is_parent', 'is_driver', 'created_at' , 'updated_at' , 'students'] 

        extra_kwargs = {
            'identifier':{'read_only' : True}, 
            'is_active':{'read_only' : True},
            'created_at':{'read_only' : True}, 
            'updated_at':{'read_only' : True}, 
        }

    # Inject the student of the current object to the return response
    def get_students(self, obj): 
        students = Student.objects.filter(parent=obj, channel__id=obj.channel.id)
        serializer = StudentSerializer(students, many=True)
        return  serializer.data
    

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")

    def get_updated_at(self,obj): 
        return obj.updated_at.strftime("%m-%d-%Y")






class UserSerializer(serializers.ModelSerializer):
    channel_accounts = serializers.SerializerMethodField('user_channels')
    image = serializers.SerializerMethodField('get_image')  
    class Meta:  
        model = User 
        fields = ['identifier', 'email' , 'first_name' , 'last_name', 'image','is_active', 'is_staff','is_verified', 'channel_accounts']

        extra_kwargs = {
            'identifier':{'read_only' : True}, 
            'is_active':{'read_only' : True},
            'is_active':{'read_only' : True},
            'is_verified':{'read_only' : True},
        }

    def user_channels(self,obj):
        channel = ChannelUser.objects.filter(user=obj)
        serializer = ChannelUserSerializer(channel, many=True)
        return serializer.data

    def get_image(self, obj):
        if settings.DEBUG :
            return f'http://127.0.0.1:8000{obj.image.url }'
        return f'http://buskeit.herokuapp.com{obj.image.url }'  





class ParentUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input-type': 'password'} , write_only= True)
    class Meta :
        model = User
        fields = ['identifier', 'first_name', 'last_name' , 'email' , 'password' , 'password2', 'is_staff' ]

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'password':{'write_only' : True},
            'is_staff':{'read_only' : True}, 
        }


    

class UserProfileImageSerializer(serializers.Serializer):
    image = serializers.ImageField()

class ParentRetrieveUpdateSerializer(serializers.ModelSerializer):
    children = StudentSerializer(read_only=True , many=True )
    class Meta: 
        model = User

        fields  = ['identifier','first_name', 'last_name' , 'email']

        extra_kwargs = {
            'identifier':{'read_only' : True},
        }



class UserInlineSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at')
    updated_at = serializers.SerializerMethodField('get_updated_at')
    class Meta:
        model = User 
        fields = ['identifier','first_name', 'last_name' , 'email' ,'image', 'is_active', 'is_staff','is_superuser', 'created_at', 'updated_at']

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")

    def get_updated_at(self,obj): 
        return obj.updated_at.strftime("%m-%d-%Y")




class StudentParentInlineSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at') 
    updated_at = serializers.SerializerMethodField('get_updated_at') 

    class Meta:  
        model = ChannelUser
        fields = ['identifier','first_name', 'last_name','email', 'is_parent','is_admin', 'is_staff' , 'created_at' , 'updated_at']

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

class StudentSerializer(serializers.ModelSerializer):
    parent = StudentParentInlineSerializer(read_only=True)
    parent_email = serializers.EmailField(write_only=True)
    created_at = serializers.SerializerMethodField('get_created_at')
    # updated_at = serializers.SerializerMethodField('get_updated_at')
    class Meta :
        model = Student
        fields = ['identifier', 'first_name','last_name','middle_name',  'parent', 'parent_email' , 'created_at']

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'created_at':{'read_only' : True},
            'parent':{'read_only' : True},
        }

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")

    
class StudentFullDetailSerializer(serializers.ModelSerializer):
    parent = StudentParentInlineSerializer(read_only=True)
    created_at = serializers.SerializerMethodField('get_created_at')
    channel = ChannelsInSerializer(read_only=True)
    # updated_at = serializers.SerializerMethodField('get_updated_at')
    class Meta :
        model = Student
        fields = ['identifier', 'first_name','last_name','middle_name',  'parent' ,'channel', 'created_at']

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'created_at':{'read_only' : True},
            'parent':{'read_only' : True},
        }

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")
    









class ResetPasswordRequestEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    class Meta:
        fields =  ['email']



class UserVettingSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=False)
    number = serializers.CharField(allow_blank=False)

    class Meta:
        fields = [ 'email' , 'number']


class SetNewPasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(min_length=1,max_length=30, write_only=True , style={'input-type': 'password'} )
    password2 = serializers.CharField(min_length=1,max_length=30, write_only=True , style={'input-type': 'password'} )
    
    class Meta:
        fields = ['password', 'password2']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True , style={'input-type': 'password'} )
    password1 = serializers.CharField(required=True , style={'input-type': 'password'} )
    password2 = serializers.CharField(required=True , style={'input-type': 'password'} )


 
"""
SIGN UP SERIALIZER FOR PARENTS / GUARDIANS 
"""
class ClientRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    phone_number = serializers.CharField(allow_blank=True)
    gender = serializers.CharField(allow_blank=True)



class UserEmailPremblyConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=False) 
    password1 = serializers.CharField(style={'input-type': 'password'}  , allow_blank=False) 
    password2 = serializers.CharField(style={'input-type': 'password'}  , allow_blank=False) 

class UserAccountActivationCodeConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=False) 
    code = serializers.CharField(allow_blank=False) 


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)