from .models import User , Student 
from rest_framework import serializers
from rest_framework import status 
# from schools.serializers import *



class UserSerializer(serializers.ModelSerializer):
    # school = SchoolInlineSerializer(read_only=True , many=True) 
    class Meta:
        model = User
        fields = ['identifier', 'email' , 'first_name' , 'last_name','is_staff']

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_active':{'read_only' : True},
        }
        


class ManagementRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        field = [ 'first_name', 'last_name' , 'email' , 'password' ]


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



class StudentSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at')
    class Meta:
        model = Student
        fields =['identifier', 'first_name' , 'last_name', 'created_at']

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y") 


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
        fields = ['identifier','first_name', 'last_name' , 'email' ,'is_active', 'is_staff','is_superuser', 'created_at', 'updated_at']

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")

    def get_updated_at(self,obj): 
        return obj.updated_at.strftime("%m-%d-%Y")



class StudentSerializer(serializers.ModelSerializer):
    # parent = ParentInlineSerializer(read_only=True)
    created_at = serializers.SerializerMethodField('get_created_at')
    # updated_at = serializers.SerializerMethodField('get_updated_at')
    class Meta :
        model = Student
        fields = ['identifier', 'first_name','last_name','middle_name',  'parent' , 'created_at']

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
    first_name = serializers.CharField(allow_blank=False)
    last_name = serializers.CharField(allow_blank=False)
    phone_number = serializers.CharField(allow_blank=False)
    gender = serializers.CharField(allow_blank=False)



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