from .models import School
from accounts.serializers import (
    StudentSerializer , UserInlineSerializer , UserSerializer ,
    ParentInlineSerializer , StudentSerializer
)
from accounts.models import Parent, Student , User     
from rest_framework import serializers



class SchoolSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField('school_students')
    parents = serializers.SerializerMethodField('school_parents') 
    created_at = serializers.SerializerMethodField('get_created_at') 
    class Meta:
        model = School
        fields = ['identifier','name', 'address' , 'is_active','is_verified' ,'created_at','students', 'parents'] 


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
        