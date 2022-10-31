from django.http import HttpResponse
from django.shortcuts import render
from accounts.models import User , School  , Parent
from accounts.serializers import ParentSerializer , ParentRetrieveUpdateSerializer , ParentInlineSerializer
from .models import School
from .serializers import SchoolSerializer
from django.contrib.auth import get_user_model

from rest_framework import generics , status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response




from rest_framework import generics

# Create your views here.
CustomUser = get_user_model()



def index(request):
    users = User.objects.all()
    students = User.objects.all()
    school = School.objects.get(id=1)
    for model in students:
        print(model.school) 
        # school.students.set(model)
        # model.school.add(school)
    return HttpResponse('Hello')




class SchoolListCreateApiView(generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
 

class SchoolRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView): 
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    lookup_field = 'identifier'



class SchoolParentListCreateAPIView(generics.ListAPIView):
    queryset = Parent.objects.all()
    serializer_class = ParentInlineSerializer

    def get(self, request, school_identifier , *args, **kwargs):
        """
            Using the school identifier provided in the url retrieve the school
            Then query all the parent in the school
        """
        try:
            school = School.objects.get(identifier=school_identifier)
            school_identifier = school.identifier
            school.parent_schools
        except School.DoesNotExist:
            return Response({'error' : 'School does not exist' } , status=status.HTTP_400_BAD_REQUEST )
        parents = school.parent_schools
        serializer = self.get_serializer(parents , many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)



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