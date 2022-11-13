from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from accounts.models import User ,  Student , ChannelUser
from accounts.serializers import StudentSerializer , StudentFullDetailSerializer
from accounts.utils import PremblyServices
from accounts.mail_services import MailServices
from accounts.permissions import IsAccountVerified

from .models import  Channel  , StudentPickUpVerification , ChannelActivationCode 
from .permissions import IsStudentParent , IsStudentParentOrChannelStaff , IsChannelAdmin
from .paginations import CustomPagination
from .serializers import  (
    ChannelsSerializer , ChannelJoinSerializer , StudentPickUpVerificationHistorySerializer,
     ChannelUserSerializer , ChannelUserFullDetailSerializer , ChannelActivationCodeConfirmSerializer ,
     ChannelUserUploadFileSerializer , MapStudentsToParentSerializer
)

from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework import generics , status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

import datetime
from threading import Thread
import string
import random
import pandas as pd
import re

# Create your views here.
CustomUser = get_user_model()


def index(request):
    redirect('')
    return HttpResponse('Hello')



class ChannelsListCreateApiView(generics.ListCreateAPIView): 
    permission_classes = [IsAuthenticated]
    queryset = Channel.objects.all()
    serializer_class = ChannelsSerializer  
    
    @swagger_auto_schema(
        operation_description='Get a list of all the available channels',
        operation_summary='Get a list of all the available channels'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description='Create new channel the required fields are :\nName\nRc_number\nPhone number and \nAddress',
        operation_summary='Create new workspace'
    )
    def post(self, request, *args, **kwargs):
        if request.user.is_verified == False:
            return Response({'detail': 'You do not have permission to perform this action'}, status=status.HTTP_401_UNAUTHORIZED )
        user = User.objects.get(id=request.user.id) 
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True) 
        name = serializer.validated_data['name']
        rc_number = serializer.validated_data['rc_number']  
        phone_number = serializer.validated_data['phone_number']
        address = serializer.validated_data['address']
        verify_channel = PremblyServices.channel_creation_verification(rc_number)
        if verify_channel == None :
            return Response({'success':False , 'detail':'Workspace cannot be created at this moment, try again later.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if verify_channel['verification']['status'] == 'NOT-VERIFIED' :
            return Response({'success': False , 'detail': 'Workspace cannot be created, because RC_NUMBER is not valid'} , status=status.HTTP_400_BAD_REQUEST )

        if verify_channel['verification']['status'] == 'PENDING' :
            return Response({'success': False , 'detail': 'Workspace cannot be created'} , status=status.HTTP_400_BAD_REQUEST )
        
        if verify_channel['data']['email_address'] :
            channel = Channel.objects.create(name=name, address=address , email = verify_channel['data']['email_address'],  rc_number=rc_number , phone_number=phone_number )
            code = ''.join(random.choice(string.digits) for _ in range(4))
            ChannelActivationCode.objects.create(email=verify_channel['data']['email_address'], code=int(code), user=user)
            Thread(target=MailServices.channel_creation_verification_email , kwargs={
                        'email': verify_channel['data']['email_address'] , 'code' : code
            }).start()
            admin = ChannelUser.objects.create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email , is_admin=True, is_staff=True , channel=channel)
            return Response( {  
                'success': True , 
                'detail' :'Workspace activation code as been sent to the school mail',
                'email': verify_channel['data']['email_address']
                }, status=status.HTTP_200_OK  )
        return Response({'success': False , 'detail': 'Workspace cannot be created'} , status=status.HTTP_400_BAD_REQUEST )

class ChannelActivationCodeConfirmApiView(generics.GenericAPIView):
    serializer_class = ChannelActivationCodeConfirmSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Activate channel with the verification code sent to the school mail',
        operation_summary='Activate a channel'
    )
    def post(self, request) :
        data = request.data
        user = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        is_code_valid = ChannelActivationCode.objects.filter(email=email, code=int(code) , user=user)
        if is_code_valid:
            channel = Channel.objects.get(email=email)
            channel.is_verified = True
            channel.save()
            is_code_valid.first().delete()
            serializer = ChannelsSerializer(channel)
            return Response( serializer.data , status=status.HTTP_200_OK)
        return Response({'success':False ,'detail': 'Channel activation code is invalid'} , status=status.HTTP_400_BAD_REQUEST)

class ChannelsRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Channel.objects.all()
    serializer_class =ChannelsSerializer
    permission_classes = [IsAuthenticated ]
    lookup_field = 'identifier'

    @swagger_auto_schema(
        operation_description='Retrieve a channel with the provided channel identifier',
        operation_summary='Retrieve a channel'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description='Delete a channel with the provided channel identifier',
        operation_summary='Delete a channel'

    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class ChannelUserJoinApiView(generics.GenericAPIView):
    serializer_class = ChannelJoinSerializer
    permission_classes =[ IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Join a channel using the channel invitation code',
        operation_summary='Join a channel with the channel invitation code'
    )
    def post(self, request):            
        try: 
            user = User.objects.get(id=request.user.id)
        except:
            return Response({'success':False ,'detail': "Access denied"} , status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        serializer = self.serializer_class(data=data) 
        if serializer.is_valid(raise_exception=True):
            try: 
                channel = Channel.objects.get(invitation_code=serializer.validated_data['invitation_code'])
            except:
                return Response({'success':False ,'detail': 'Channel invitation code is not valid'} , status=status.HTTP_400_BAD_REQUEST)
            
            channel_user_exist = ChannelUser.objects.filter(email=request.user.email, channel=channel)
            if channel_user_exist.exists():
                channel_user = channel_user_exist.first()
                channel_user.user = user
                channel_user.save()
                return Response({'success':False ,'detail': 'You are now in the channel'} , status=status.HTTP_200_OK)
            return Response({'success':False ,'detail': "Your data is not available in the channel! Contact the school admin"} , status=status.HTTP_401_UNAUTHORIZED)

class ChannelStudentListCreateApiView(generics.ListCreateAPIView): 
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = CustomPagination 
 
    def get_queryset(self):
        student = Student.objects.filter(channel__identifier=self.kwargs.get('identifier'))
        return student
  
    #  get the student of provided channel identifier\
    @swagger_auto_schema(
        operation_summary='Retrieve channel students list'
    )
    def get(self, request , identifier ):
        try:
            Channel.objects.get(identifier=identifier)
        except Channel.DoesNotExist:
            return Response({'success':False ,'detail': 'Channel does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        query = self.get_queryset()
        page = self.paginate_queryset(query)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(query, many=True)
        return  Response(serializer.data , status=status.HTTP_200_OK) 


    @swagger_auto_schema(
        operation_summary='Add new student to a channel'
    )
    def post(self, request , identifier ):
        try:
            channel = Channel.objects.get(identifier=identifier)
        except:
            return Response({'success':False ,'detail': 'Channel does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            first_name = serializer.validated_data.get('first_name', None )
            last_name = serializer.validated_data.get('last_name', None )
            middle_name = serializer.validated_data.get('middle_name', None )
            student = Student.objects.create(first_name=first_name , last_name=last_name , middle_name=middle_name , channel=channel )
            return Response(self.serializer_class(student).data , status=status.HTTP_201_CREATED)

class ChannelParentsListCreateAPIView(generics.ListCreateAPIView):
    queryset = ChannelUser.objects.all()
    serializer_class = ChannelUserSerializer
    pagination_class = CustomPagination 

    def get_queryset(self):
        channel = ChannelUser.objects.filter(channel__identifier=self.kwargs.get('identifier'), is_parent=True)
        return channel
  
    #  get the parent of provided channel identifier
    @swagger_auto_schema(
        operation_summary='Retrieve a channel parents list'
    )
    def get(self, request , identifier ):
        try:
            Channel.objects.get(identifier=identifier)
        except Channel.DoesNotExist:
            return Response({'success':False ,'detail': 'Channel does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        query = self.get_queryset()
        page = self.paginate_queryset(query)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(query, many=True)
        return  Response(serializer.data , status=status.HTTP_200_OK) 


    def post(self, request , identifier ):
        try:
            channel = Channel.objects.get(identifier=identifier)
        except:
            return Response({'success':False ,'detail': 'Channel does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            first_name = serializer.validated_data.get('first_name', None )
            last_name = serializer.validated_data.get('last_name', None )
            email = serializer.validated_data.get('email', None )
            if ChannelUser.objects.filter(email=email, channel=channel).exists():
                return Response({'success': False , 'detail':'Email already exist'} , status=status.HTTP_400_BAD_REQUEST )
            new_user = ChannelUser.objects.create(first_name=first_name , last_name=last_name ,email=email , channel=channel, is_parent=True )
            return Response(self.serializer_class(new_user).data , status=status.HTTP_201_CREATED)


class MapStudentsToParentApiView(generics.GenericAPIView):
    serializer_class  = MapStudentsToParentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        # method='POST', 
        operation_description='To map a students to parent\nFirst you need the channel identifier ( channel_identifier), then the parent identifier (channel_user_identifier)\nA list of students identifier as the body of the request.',
        operation_summary='This endpoint map students to parent',

    ) 
    def post(self, request, channel_identifier , channel_user_identifier ):
        try:
            channel = Channel.objects.get(identifier=channel_identifier)
        except Channel.DoesNotExist:
            return Response({'success': False , 'detail':'Channel does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        if ChannelUser.objects.filter(user__id=request.user.id, channel=channel , is_admin=True) :
            try:
                user = ChannelUser.objects.get(identifier=channel_user_identifier)
            except ChannelUser.DoesNotExist :
                return Response({'success': False, 'detail':'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            for student_identifier in serializer.validated_data['students']:
                try:
                    student = Student.objects.get(identifier=student_identifier)
                    print(student.first_name)
                except Student.DoesNotExist:
                    return Response({'success': False, 'detail':'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    # ["ST2K3Y72YALSDF2","STDQG4CDYHVZWPA","STJ82ZV8NP7EDNK"]
                student.parent = user
                student.save()
                detail = f'All the students has been mapped to {user.first_name}'
            # return Response({'success': True, 'detail': detail } ,status=status.HTTP_200_OK)
        return Response({'success': True, 'detail': 'You do not have permission to perform this action' } ,status=status.HTTP_401_UNAUTHORIZED)
        




# This view handle the current day verified picked students
class ChannelVerifiedPickedStudentsAPIView(generics.ListAPIView):
    queryset = StudentPickUpVerification.objects.all()
    serializer_class = StudentPickUpVerificationHistorySerializer

    def get_queryset(self):
        return StudentPickUpVerification.objects.filter(date=datetime.datetime.now().date() , student__channel__identifier=self.kwargs.get('identifier'))






class ChannelParentKidsListAPIView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    """"
    Get the list of the user kids in a specific channel 
    using the channel identifier and the channel user identifier 
    """

    @swagger_auto_schema(
        operation_summary='Retrieve parent children in a channel',
        operation_description='Get the list of the user kids in a specific channel\nusing the channel identifier and the channel user identifier '
    )
    def get(self, request , channel_identifier , channel_user_identifier ): 
        try:
            channel = Channel.objects.get(identifier=channel_identifier)
        except:
            return Response({'success':False ,'message': 'School does not exist'} , status=status.HTTP_404_NOT_FOUND)
        try:
            user = ChannelUser.objects.get(identifier=channel_user_identifier)
        except:
            return Response({'success':False ,'message': 'Channel user does not exist'} , status=status.HTTP_404_NOT_FOUND)
        students = self.queryset.filter(channel=channel , parent=user)
        serializer = self.serializer_class(students , many=True) 
        return  Response(serializer.data , status=status.HTTP_200_OK) 


class ChannelUsersRetrieveUpdateDestroyAPIView(generics.GenericAPIView):
    serializer_class = ChannelUserFullDetailSerializer

    @swagger_auto_schema(
        operation_summary='Retrieve the list of users in a specific channel'
    )
    def get(self, request , channel_identifier , channel_user_identifier ):
        try:
            channel = Channel.objects.get(identifier=channel_identifier)
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

    @swagger_auto_schema(
        operation_summary='Retrieve the list of a parent children'
    )
    def get(self, request , channel_identifier ):
        user = User.objects.get(id=request.user.id)
        try:
            channel = Channel.objects.get(identifier=channel_identifier)
        except:
            return Response({'success':False ,'message': 'Channel does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        students = self.queryset.filter(channel=channel , parent__user__id=user.id)
        serializer = self.serializer_class( students , many=True)
        return  Response(serializer.data , status=status.HTTP_200_OK) 


class StudentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView) : 
    # This view allow only the students parent or channel staff to view detail
    permission_classes = [IsAuthenticated , IsStudentParentOrChannelStaff ]
    serializer_class = StudentFullDetailSerializer
    queryset = Student.objects.all()
    lookup_field = 'identifier'


    @swagger_auto_schema(
        operation_summary='Retrieve student profile'
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update student profile'
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary=''
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete student'
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class StudentPickUpVerificationApiView(generics.RetrieveAPIView) :
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated , IsStudentParent]
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    lookup_field = 'identifier'
    
    @swagger_auto_schema(
        operation_summary='Verify student pick up'
    )
    def get(self, request, *args, **kwargs):
        student = self.get_object()
        if StudentPickUpVerification.objects.filter(date=datetime.datetime.now().date() , student=student ).exists(): 
            return Response({'success': True ,'message': 'Student already verify'} ,status=status.HTTP_200_OK) 
        StudentPickUpVerification.objects.create(student=student)
        return Response({'success': True ,'message': 'Successful verification'} , status=status.HTTP_200_OK) 


class StudentPickUpVerificationHistoryApiView(generics.GenericAPIView) :
    permission_classes = [IsAuthenticated , IsStudentParentOrChannelStaff ]
    serializer_class = StudentPickUpVerificationHistorySerializer
    queryset = StudentPickUpVerification.objects.all()
    lookup_field = 'identifier'
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_summary='Retrieve student pick up record'
    )
    def get(self, request, identifier):
        query = StudentPickUpVerification.objects.filter(student__identifier=identifier)
        page = self.paginate_queryset(query)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(query, many=True)
        return Response( serializer.data , status=status.HTTP_200_OK) 

    

class ChannelUserUploadCsvApiView(generics.CreateAPIView):
    queryset = ChannelUser.objects.all()
    serializer_class = ChannelUserUploadFileSerializer
    permission_classes = [IsAuthenticated, IsChannelAdmin]


    @swagger_auto_schema(
        operation_summary='Upload parent via csv file',
        operation_description='The format should be first name , last name and email'
    )
    def post(self, request, identifier , *args, **kwargs):
        try:
            channel = Channel.objects.get(identifier=identifier)
        except:
            return Response({'success':False , 'detail':'Channel does not exist'})
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file)
        for _ , row in reader.iterrows():
            try:
                first_name = row['Staff Sname']
                last_name = row['Staff Oname']
                # This is a dummy sample creating user mail with the first name and the index of user in row
                email = f'{first_name}{str(_)}@gmail.com'
                pattern = re.compile(r'\s+')
                email = re.sub(pattern,'', email) 
            except:
                return Response({'success':False, 'detail':'Invalid csv format'}, status=status.HTTP_400_BAD_REQUEST)
            user_exist = ChannelUser.objects.filter(email=email,channel=channel)
            if user_exist:
                user_exist.is_parent = True
                user_exist.save()
            else:
                new_user = ChannelUser.objects.create(first_name=first_name ,last_name=last_name , email=email , is_parent=True , channel=channel )
                new_user.save()

        return Response({'success': True ,'detail':'User uploaded successfully' }, status=status.HTTP_201_CREATED)


class ChannelStudentUploadCsvApiView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = ChannelUserUploadFileSerializer
    permission_classes = [IsAuthenticated, IsChannelAdmin ]

    @swagger_auto_schema(
        operation_summary='Upload student via csv file',
        operation_description='The format should be first name , last name'
    )
    def post(self, request, identifier , *args, **kwargs):
        try:
            channel = Channel.objects.get(identifier=identifier)
        except:
            return Response({'success':False , 'detail':'Channel does not exist'})
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file)
        for _ , row in reader.iterrows():
            try:
                # first_name = row[3] 
                first_name = row['Staff Sname']  
                # last_name = row[1]
                last_name = row['Staff Oname']
                print(first_name , last_name )
            except:
                return Response({'success':False, 'detail':'Invalid csv format'}, status=status.HTTP_400_BAD_REQUEST)
            new_user = Student.objects.create(first_name=first_name ,last_name=last_name ,channel=channel )
            new_user.save()
        return Response({'success': True ,'detail':'Student uploaded successfully' }, status=status.HTTP_201_CREATED)
    
