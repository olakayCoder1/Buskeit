from django.http import HttpResponse
from django.shortcuts import render
from accounts.models import User , School  , Parent , Student
from accounts.serializers import ParentSerializer , ParentRetrieveUpdateSerializer , ParentInlineSerializer , StudentSerializer
from .models import School
from .serializers import SchoolSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework import generics , status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema



from rest_framework import generics

# Create your views here.
CustomUser = get_user_model()



def index(request):
    users = User.objects.all()
    students = User.objects.all()
    school = School.objects.get(id=1)
    return HttpResponse('Hello')




class SchoolListCreateApiView(generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
 
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class SchoolRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView): 
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    lookup_field = 'identifier'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)



class SchoolParentListCreateAPIView(generics.ListAPIView):
    queryset = Parent.objects.all()
    serializer_class = ParentInlineSerializer


    """
            Using the school identifier provided in the url retrieve the school
            Then query all the parent in the school
    """
    @swagger_auto_schema(
        operation_summary='List all schools parents',
        operation_description='This endpoint return the list of parents in all the schools on the plateform'
    )
    def get(self, request, school_identifier , *args, **kwargs):
        try:
            school = School.objects.get(identifier=school_identifier)
            school_identifier = school.identifier
            school.parent_schools
        except School.DoesNotExist:
            return Response({'error' : 'School does not exist' } , status=status.HTTP_400_BAD_REQUEST )
        parents = school.parent_schools
        serializer = self.get_serializer(parents , many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)


class SchoolStudentsListCreateAPIView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def get(self, request, school_identifier , *args, **kwargs):
        """
            Using the school identifier provided in the url retrieve the school
            Then query all the students in the school
        """
        try:
            school = School.objects.get(identifier=school_identifier)
            school_identifier = school.identifier
            school.parent_schools
            students = Student.objects.filter(school=school)
        except School.DoesNotExist:
            return Response({'error' : 'School does not exist' } , status=status.HTTP_400_BAD_REQUEST ) 
        serializer = self.get_serializer(students , many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)


    def post(self, request , school_identifier , *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            try:
                school = School.objects.get(identifier=school_identifier)
                students = Student.objects.create(first_name=first_name, last_name=last_name , school=school)
            except School.DoesNotExist:
                return Response({'error' : 'School does not exist' } , status=status.HTTP_400_BAD_REQUEST ) 
            serializer = self.get_serializer(students)
        return Response(serializer.data , status=status.HTTP_201_CREATED)

 


class SchoolStudentRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def get(self, request,  school_identifier , student_identifier , *args, **kwargs):
        try:
            student = Student.objects.get(identifier=student_identifier)
        except Student.DoesNotExist:
            return Response({'error' : 'Student does not exist' } , status=status.HTTP_400_BAD_REQUEST ) 
        serializer = self.get_serializer(student)
        return Response(serializer.data , status=status.HTTP_200_OK)

    
    def delete(self, request , school_identifier , student_identifier , *args, **kwargs):
        try:
            student = Student.objects.get(identifier=student_identifier)
        except Student.DoesNotExist:
            return Response({'error' : 'Student does not exist' } , status=status.HTTP_400_BAD_REQUEST ) 
        student.delete() 
        return Response(status=status.HTTP_200_OK) 



class SchoolParentRetrieveUpdateAPIView(generics.ListAPIView):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer 

    def get(self, request, school_identifier , *args, **kwargs):
        try:
            school = School.objects.get(identifier=school_identifier)
        except School.DoesNotExist:
            return Response({'error' : 'School does not exist' } , status=status.HTTP_400_BAD_REQUEST )
        users = User.objects.filter()
        users = school.user_schools
        print(users)
        serializer = self.get_serializer(users , many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)