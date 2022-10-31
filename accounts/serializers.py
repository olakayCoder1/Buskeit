from .models import User , Student , Parent , SchoolAdmin
from rest_framework import serializers
from schools.models import School
from rest_framework import status 
# from schools.serializers import *



class SchoolInlineSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_at') 
    class Meta:
        model = School
        fields = ['identifier','name', 'address' , 'is_active','is_verified' ,'created_at']


        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_active':{'read_only' : True},
            'is_verified':{'read_only' : True}, 
        }

    def get_created_at(self,obj): 
        return obj.created_at.strftime("%m-%d-%Y")


class UserSerializer(serializers.ModelSerializer):
    school = SchoolInlineSerializer(read_only=True , many=True)
    class Meta:
        model = User
        fields = ['identifier', 'email' , 'first_name' , 'last_name', 'is_parent', 'is_school_admin','is_staff']

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
    school = SchoolInlineSerializer(read_only=True , many=True)
    class Meta :
        model = User
        fields = ['identifier', 'first_name', 'last_name' , 'email' , 'password' , 'password2', 'is_parent', 'is_school_admin','is_staff'  ,'school' ]

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'password':{'write_only' : True},
            'is_management':{'read_only' : True},
            'is_parent':{'read_only' : True},
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

        fields  = ['identifier','first_name', 'last_name' , 'email', 'is_parent' , 'is_management', 'children']

        extra_kwargs = {
            'identifier':{'read_only' : True},
            'is_management':{'read_only' : True},
            'is_parent':{'read_only' : True},
            'is_staff':{'read_only' : True},  
        }



class UserInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ['identifier','first_name', 'last_name' , 'email' ,'is_parent','is_school_admin','is_active', 'is_staff','is_superuser', 'created_at']


class SchoolAdminSerializer(serializers.ModelSerializer):
    user = UserInlineSerializer(read_only=True)
    class Meta:
        model = SchoolAdmin
        fields = ['user','nin_number','is_owner', 'is_verified' ]
    

#School admin model serializer 
class SchoolAdminInlineSerializer(serializers.ModelSerializer):
    user = UserInlineSerializer(read_only=True)
    class Meta:
        model = SchoolAdmin
        fields = ['user','nin_number','is_owner', 'is_verified' ]



class ParentInlineSerializer(serializers.ModelSerializer):
    user = UserInlineSerializer(read_only=True)
    class Meta :
        model = Parent
        fields = ['user','address','phone_number','nin_number','is_verified']


class ParentSerializer(serializers.ModelSerializer):
    user = UserInlineSerializer(read_only=True)
    class Meta :
        model = Parent
        fields = ['user','address','phone_number','nin_number','is_verified','schools']



class StudentSerializer(serializers.ModelSerializer):
    class Meta :
        model = Student
        fields = ['identifier', 'first_name','last_name', 'parent' , 'created_at']






class ResetPasswordRequestEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    class Meta:
        fields =  ['email']



class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=1,max_length=30, write_only=True)
    password2 = serializers.CharField(min_length=1,max_length=30, write_only=True)
    
    class Meta:
        fields = ['password', 'password2']

class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


    def save(self):
        request = self.context.get('request')
        old_password = self.validated_data['old_password']
        new_password = self.validated_data['new_password']
        user = User.objects.get(id=request.user.id)
        if not user.check_password(old_password):
            raise serializers.ValidationError({'error': 'Incorrect password','status': status.HTTP_400_BAD_REQUEST})
        user.set_password(new_password)
        user.save()
        return user


"""
SIGN UP SERIALIZER FOR PARENTS / GUARDIANS 
"""
class ClientRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(allow_blank=False)
    last_name = serializers.CharField(allow_blank=False)
    email = serializers.CharField(allow_blank=False)
    phone_number = serializers.CharField(style={'input-type':'number'}, allow_blank=False)
    password1 = serializers.CharField(style={'input-type': 'password'} , allow_blank=False)
    password2 = serializers.CharField(style={'input-type': 'password'}  , allow_blank=False)


    