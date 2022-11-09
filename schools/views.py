from django.http import HttpResponse
from django.shortcuts import render
from accounts.models import User , School  , Parent , Student , ChannelUser
from accounts.serializers import (
    ParentSerializer , ParentRetrieveUpdateSerializer , 
    ParentInlineSerializer , StudentSerializer 

)
from .models import School , Channel  , StudentPickUpVerification
from .permissions import IsStudentParent , IsStudentParentOrChannelStaff
from .serializers import  (
    SchoolSerializer , ChannelsSerializer , ChannelJoinSerializer ,
     ChannelUserSerializer , ChannelUserFullDetailSerializer , StudentStudentPickUpVerificationHistorySerializer
)
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework import generics , status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
import datetime


from rest_framework import generics

# Create your views here.
CustomUser = get_user_model()

"""
!!! TODO => renaming all the school variable to channel
"""

def index(request):
    # users = User.objects.all() 
    # students = User.objects.all()
    # school = School.objects.get(id=1)
    return HttpResponse('Hello')

class ChannelsListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Channel.objects.all()
    serializer_class = ChannelsSerializer
 
    def post(self, request, *args, **kwargs):
        # admin = User.objects.get(id=request.id) 
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ChannelsRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Channel.objects.all()
    serializer_class =ChannelsSerializer
    lookup_field = 'identifier'

class ChannelUserJoinApiView(generics.GenericAPIView):
    serializer_class = ChannelJoinSerializer

    def get(self, request, invitation_code):            
        try: 
            user = User.objects.get(id=request.id) 
        except:
            return Response({'success':False ,'message': "Access denied"} , status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        serializer = self.serializer_class(data=data) 
        if serializer.is_valid(raise_exception=True):
            try: 
                channel = Channel.objects.get(invitation_code=invitation_code)
                # channel = Channel.objects.get(invitation_code=serializer.validated_data['invitation_code'])
            except:
                return Response({'success':False ,'message': 'School does not exist'} , status=status.HTTP_400_BAD_REQUEST)
            
            if ChannelUser.objects.filter(user=user, channel=channel).exists():
                return Response({'success':False ,'message': 'You are already in the channel'} , status=status.HTTP_200_OK)
            ChannelUser.objects.create(user=user, channel=channel)
        return Response({'success':True }, status=status.HTTP_200_OK)  


class ChannelStudentListCreateApiView(generics.GenericAPIView): 
    serializer_class = StudentSerializer
 
    def get_queryset(self):
        student = Student.objects.filter(channel__identifier=self.kwargs.get('school_identifier'))
        if student.exists():
            return student
        return None
        
    #  get the student of provided channel identifier
    def get(self, request , school_identifier ):
        query = self.get_queryset()
        if query == None :
            return Response({'success':False ,'message': 'School does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(query , many=True)
        return  Response(serializer.data , status=status.HTTP_200_OK) 


    def post(self, request , school_identifier ):
        try:
            channel = Channel.objects.get(identifier=self.kwargs.get('school_identifier'))
        except:
            return Response({'success':False ,'message': 'School does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            first_name = serializer.validated_data.get('first_name', None )
            last_name = serializer.validated_data.get('last_name', None )
            middle_name = serializer.validated_data.get('middle_name', None )
            student = Student.objects.create(first_name=first_name , last_name=last_name , middle_name=middle_name , channel=channel )
            return Response(self.serializer_class(student).data , status=status.HTTP_201_CREATED)

class ChannelUsersListAPIView(generics.ListAPIView):
    queryset = ChannelUser.objects.all()
    serializer_class = ChannelUserSerializer

    def get(self, request , school_identifier ):
        try:
            channel = Channel.objects.get(identifier=school_identifier)
        except:
            return Response({'success':False ,'message': 'School does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        users = ChannelUser.objects.filter(channel=channel)
        serializer = self.serializer_class(users , many=True)
        return  Response(serializer.data , status=status.HTTP_200_OK) 


class ChannelUsersRetrieveUpdateDestroyAPIView(generics.GenericAPIView):
    serializer_class = ChannelUserFullDetailSerializer

    def get(self, request , school_identifier , channel_user_identifier ):
        try:
            channel = Channel.objects.get(identifier=school_identifier)
        except:
            return Response({'success':False ,'message': 'School does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        user_query = ChannelUser.objects.filter(channel=channel, identifier=channel_user_identifier)
        if user_query.exists():
            user = user_query.first()
            serializer = self.serializer_class(user)
            return Response(serializer.data ,  status=status.HTTP_200_OK)
        # serializer = self.serializer_class(users , many=True)
        return  Response({'success':False ,'message': 'User not in  does not exist in channels'} , status=status.HTTP_400_BAD_REQUEST) 


class ChannelParentKidsListAPIView(generics.ListAPIView):
    # this view return the list parent kids
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request , school_identifier ):
        user = User.objects.get(id=request.user.id)
        for m in Student.objects.all():
            # print(m.channel.id)
            print(m.parent.user.id)
        # user = User.objects.get(id=5)
        try:
            channel = Channel.objects.get(identifier=school_identifier)
        except:
            return Response({'success':False ,'message': 'School does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        students = self.queryset.filter(channel=channel , parent__user__id=user.id)
        serializer = self.serializer_class( students , many=True)
        return  Response(serializer.data , status=status.HTTP_200_OK) 


class StudentRetrieveUpdateDestroyAPIView(generics.RetrieveAPIView) :
    # This view allow only the students parent or channel staff to view detail
    permission_classes = [IsAuthenticated , IsStudentParentOrChannelStaff ]
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    lookup_field = 'identifier'


class StudentPickUpVerificationApiView(generics.RetrieveAPIView) :
    permission_classes = [IsAuthenticated , IsStudentParent]
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    lookup_field = 'identifier'

    def get(self, request, *args, **kwargs):
        student = self.get_object()
        if StudentPickUpVerification.objects.filter(date=datetime.datetime.now().date() , student=student ).exists(): 
            return Response({'success': True ,'message': 'Student already verify'} ,status=status.HTTP_200_OK) 
        StudentPickUpVerification.objects.create(student=student)
        return Response({'success': True ,'message': 'Successful verification'} , status=status.HTTP_200_OK) 


class StudentPickUpVerificationHistoryApiView(generics.GenericAPIView) :
    permission_classes = [IsAuthenticated , IsStudentParentOrChannelStaff ]
    serializer_class = StudentStudentPickUpVerificationHistorySerializer
    queryset = StudentPickUpVerification.objects.all()
    lookup_field = 'identifier'

    def get(self, request, identifier):
        query = StudentPickUpVerification.objects.filter(student__identifier=identifier)
        serializer = self.serializer_class(query , many=True)
        return Response( serializer.data , status=status.HTTP_200_OK) 

    








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