from django.shortcuts import render , redirect
from django.http import HttpResponse
from accounts.models import User ,  Student , ChannelUser
from accounts.serializers import StudentSerializer 
from accounts.utils import PremblyServices
from accounts.mail_services import MailServices
from accounts.permissions import IsAccountVerified
from .models import  Channel  , StudentPickUpVerification , ChannelActivationCode
from .permissions import IsStudentParent , IsStudentParentOrChannelStaff , IsChannelAdmin
from .paginations import CustomPagination
from .serializers import  (
    ChannelsSerializer , ChannelJoinSerializer , StudentPickUpVerificationHistorySerializer,
     ChannelUserSerializer , ChannelUserFullDetailSerializer , ChannelActivationCodeConfirmSerializer ,
     ChannelUserUploadFileSerializer
)
from django.contrib.auth import get_user_model
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

"""
!!! TODO => renaming all the school variable to channel
"""

def index(request):
    redirect('')
    return HttpResponse('Hello')



class ChannelsListCreateApiView(generics.ListCreateAPIView): 
    permission_classes = [IsAuthenticated]
    queryset = Channel.objects.all()
    serializer_class = ChannelsSerializer  
 
    def post(self, request, *args, **kwargs):
        if request.user.is_verified == False:
            return Response({'detail': 'You do not have permission to perform this action'}, status=status.HTTP_401_UNAUTHORIZED )
        user = User.objects.get(id=request.user.id) 
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True) 
        name = serializer.validated_data['name']
        rc_number = serializer.validated_data['rc_number']
        company_type = serializer.validated_data['company_type']
        email = serializer.validated_data['email'] 
        phone_number = serializer.validated_data['phone_number']
        address = serializer.validated_data['address']
        # verify_channel = PremblyServices.channel_creation_verification(serializer.validated_data['rc_number'])
        # if verify_channel == None :
        #     return Response({'success':False , 'detail':'RC_NUMBER is not valid'}, status=status.HTTP_400_BAD_REQUEST)
        # if verify_channel['data']['company_name'] != serializer.validated_data['name']:
        #     return Response({'success': False , 'detail': 'Company name is not correct'}, status=status.HTTP_400_BAD_REQUEST)

        # if verify_channel['data']['email_address'] != serializer.validated_data['email']:
        #     return Response({'success': False , 'detail': 'Company name is not correct'}, status=status.HTTP_400_BAD_REQUEST)

        channel = Channel.objects.create(name=name, address=address ,email=email ,  rc_number=rc_number , phone_number=phone_number , company_type=company_type)
        code = ''.join(random.choice(string.digits) for _ in range(4))
        ChannelActivationCode.objects.create(email=email, code=int(code))
        Thread(target=MailServices.channel_creation_verification_email , kwargs={
                        'email': email , 'code' : code
        }).start()
        admin = ChannelUser.objects.create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email , is_admin=True, is_staff=True , channel=channel)
        return Response( {  
                'success': True , 
                'detail' :'Channel activation code as been sent to the email',
                'email': email
                }, status=status.HTTP_200_OK  )
        # serializer = self.serializer_class(channel)
        # return Response(serializer.data, status=status.HTTP_200_OK)



class ChannelActivationCodeConfirmApiView(generics.GenericAPIView):
    serializer_class = ChannelActivationCodeConfirmSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request) :
        data = request.data
        user = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        is_code_valid = ChannelActivationCode.objects.filter(email=email, code=int(code) , user=user).exists()
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
    lookup_field = 'identifier'

class ChannelUserJoinApiView(generics.GenericAPIView):
    serializer_class = ChannelJoinSerializer
    permission_classes =[ IsAuthenticated]

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
                return Response({'success':False ,'detail': 'Channel invitation code is invalid'} , status=status.HTTP_400_BAD_REQUEST)
            
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
        if student.exists():
            return student
        return None
        
    #  get the student of provided channel identifier
    def get(self, request , identifier ):
        query = self.get_queryset()
        if query == None :
            return Response({'success':False ,'message': 'School does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(query , many=True)
        return  Response(serializer.data , status=status.HTTP_200_OK) 


    def post(self, request , identifier ):
        try:
            channel = Channel.objects.get(identifier=self.kwargs.get('identifier'))
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

    def get(self, request , channel_identifier ): 
        try:
            channel = Channel.objects.get(identifier=channel_identifier)
        except:
            return Response({'success':False ,'message': 'School does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        users = ChannelUser.objects.filter(channel=channel)
        serializer = self.serializer_class(users , many=True)
        return  Response(serializer.data , status=status.HTTP_200_OK) 



class ChannelUserKidsListAPIView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    """"
    Get the list of the user kids in a specific channel 
    using the channel identifier and the channel user identifier 
    """

    def get(self, request , channel_identifier , channel_user_identifier ): 
        try:
            channel = Channel.objects.get(identifier=channel_identifier)
        except:
            return Response({'success':False ,'message': 'School does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        try:
            user = ChannelUser.objects.get(identifier=channel_user_identifier)
        except:
            return Response({'success':False ,'message': 'Channel user does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        students = self.queryset.filter(channel=channel , parent=user)
        serializer = self.serializer_class(students , many=True) 
        return  Response(serializer.data , status=status.HTTP_200_OK) 


class ChannelUsersRetrieveUpdateDestroyAPIView(generics.GenericAPIView):
    serializer_class = ChannelUserFullDetailSerializer

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

    def get(self, request , channel_identifier ):
        user = User.objects.get(id=request.user.id)
        try:
            channel = Channel.objects.get(identifier=channel_identifier)
        except:
            return Response({'success':False ,'message': 'Channel does not exist'} , status=status.HTTP_400_BAD_REQUEST)
        students = self.queryset.filter(channel=channel , parent__user__id=user.id)
        serializer = self.serializer_class( students , many=True)
        return  Response(serializer.data , status=status.HTTP_200_OK) 


class StudentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateAPIView) : 
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
    serializer_class = StudentPickUpVerificationHistorySerializer
    queryset = StudentPickUpVerification.objects.all()
    lookup_field = 'identifier'

    def get(self, request, identifier):
        query = StudentPickUpVerification.objects.filter(student__identifier=identifier)
        serializer = self.serializer_class(query , many=True)
        return Response( serializer.data , status=status.HTTP_200_OK) 

    

class ChannelUserUploadCsvApiView(generics.CreateAPIView):
    queryset = ChannelUser.objects.all()
    serializer_class = ChannelUserUploadFileSerializer
    permission_classes = [IsAuthenticated, IsChannelAdmin]

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
                email = f'{first_name}{str(_)}@gmail.com'
                pattern = re.compile(r'\s+')
                email = re.sub(pattern,'', email) 
            except:
                return Response({'success':False, 'detail':'Invalid csv format'}, status=status.HTTP_400_BAD_REQUEST)
            new_user = ChannelUser.objects.create(first_name=first_name ,last_name=last_name , email=email , is_parent=True , channel=channel )
            new_user.save()
        
        return Response({'success': True ,'detail':'User uploaded successfully' }, status=status.HTTP_201_CREATED)


class ChannelStudentUploadCsvApiView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = ChannelUserUploadFileSerializer
    permission_classes = [IsAuthenticated, IsChannelAdmin ]

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
            except:
                return Response({'success':False, 'detail':'Invalid csv format'}, status=status.HTTP_400_BAD_REQUEST)
            new_user = Student.objects.create(first_name=first_name ,last_name=last_name ,channel=channel )
            new_user.save()
        
        return Response({'success': True ,'detail':'Student uploaded successfully' }, status=status.HTTP_201_CREATED)
    
