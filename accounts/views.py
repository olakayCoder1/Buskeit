from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics , status 
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str , force_bytes, DjangoUnicodeDecodeError, force_str
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
from api import serializers
from rest_framework.permissions import IsAuthenticated 
from .serializers import (
    ManagementRegisterSerializer,ParentUserSerializer, ChangePasswordSerializer,
    UserSerializer , ParentRetrieveUpdateSerializer , ParentSerializer,
    ResetPasswordRequestEmailSerializer , SetNewPasswordSerializer,
    ClientRegisterSerializer ,
)
from .models import (
    User , Student ,Parent , AccountActivation
)
from schools.models import School
# Create your views here.
from .utils import forget_password_mail , account_activation_mail
import asyncio
from threading import Thread

class ResetPasswordRequestEmailApiView(generics.GenericAPIView):
    serializer_class = ResetPasswordRequestEmailSerializer
 
    def post(self, request):
        email = request.data['email']
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = User.objects.get(email=email)
                uuidb64 = urlsafe_base64_encode(force_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                Thread(target=forget_password_mail, kwargs={
                    'email': user.email ,'token': token , 'uuidb64':uuidb64
                }).start()
                # send_mail  = await forget_password_mail(user.email,token ,uuidb64)
                return Response( 
                        {'success':True , 'message': 'Password reset instruction will be sent to the mail' },
                        status=status.HTTP_200_OK
                        )
            except:
                return Response( 
                    {'success':True , 'message': 'Password reset mail sent' }, 
                    status=status.HTTP_200_OK
                    )
        return Response( 
                    {'success':False , 'message': 'Enter a valid email address' }, 
                    status=status.HTTP_400_BAD_REQUEST
                    )


# This view handle changing of user password on forget password
class SetNewPasswordTokenCheckApi(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    def post(self, request, token , uuidb64 ):
        try:
            id = smart_str(urlsafe_base64_decode(uuidb64))
            user = User.objects.get(id=id)
            if PasswordResetTokenGenerator().check_token(user, token):
                data = request.data
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                user.set_password(serializer.validated_data['password'])
                user.save() 
                return Response({'success':True , 'message':'Password updated successfully'}, status=status.HTTP_200_OK)
            return Response({'success':False ,'message':'Token is not valid'}, status=status.HTTP_400_BAD_REQUEST)
        except DjangoUnicodeDecodeError as identifier:
            return Response({'success':False ,'message': 'Token is not valid'}, status=status.HTTP_400_BAD_REQUEST)


#  This view handle password update within app ( authenticated user)
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [ IsAuthenticated ] 
    model = User

    def get_object(self,queryset=None):
        obj = self.request.user
        return obj
        
    def update(self, request, *args, **kwargs):
        self.object=self.get_object()
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get('old_password')):
                return Response({'ola_password': ['wrong password']}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response={
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully','data':[]
                }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class ParentRegisterSerializerApiView(generics.GenericAPIView):
    serializer_class = ClientRegisterSerializer

    def post(self, request:Response ):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True) :
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            email = serializer.validated_data['email']
            password1 = serializer.validated_data['password1']
            password2 = serializer.validated_data['password2']
            first_name = serializer.validated_data['first_name']
            if password1 != password2 :
                return  Response({'success':False ,'message': 'Password does not match'} , status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(email=email)
                return Response({'success':False ,'message': 'Email already exists'} , status=status.HTTP_400_BAD_REQUEST)
            except:
                user = User.objects.create(first_name=first_name,last_name=last_name,email=email, is_parent=True)
                user.set_password(password2)
                user.is_active = False
                token = PasswordResetTokenGenerator().make_token(user)
                uuidb64 = urlsafe_base64_encode(force_bytes(user.id))
                Thread(target=account_activation_mail, kwargs={
                        'email': user.email ,'token': token , 'uuidb64':uuidb64
                    }).start()
                AccountActivation.objects.create(active_token=token , email=user.email)
            return Response({'success':True , 'message': 'Verification mail as been sent to the email address'},status.HTTP_200_OK)


class AccountEmailVerificationConfirmApiView(APIView):
    def get(request, uuidb64 , token ):
        try:  
            uid = force_str(urlsafe_base64_decode(uuidb64))  
            user = User.objects.get(pk=uid)  
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
            user = None  
        if user is not None and AccountActivation.objects.filter(active_token=token , email=user.email).exists():  
            token = AccountActivation.objects.filter(active_token=token , email=user.email).first()
            token.delete()
            user.is_active = True  
            user.save()  
            serializer = UserSerializer(user)
            response = serializer.data
            user_token = {'token': user.auth_token.key }
            response.update(user_token)
            return Response(response , status=status.HTTP_201_CREATED) 
          
        return Response({'success':False , 'message': 'Mail verification is invalid'},status.HTTP_200_OK)





























def home(request):
  
    return HttpResponse('HELLO WORLD')









class ParentUsersListCreateApiView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ParentUserSerializer 

    def post(self, request, *args, **kwargs):
        referrer = request.GET.get('referrer', None )
        if referrer != None :
            try:
                school = School.objects.get(identifier=referrer)
            except School.DoesNotExist :
                return Response({'error': 'School referrer link is not valid'} , status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=request.data['email'])
            except User.DoesNotExist :
                first_name = request.data['first_name']
                last_name = request.data['last_name']
                email = request.data['email']
                password = request.data['password']
                password2 = request.data['password2']
                if password == password2 :
                    return Response({'error' : 'password does not match'}, status=status.HTTP_400_BAD_REQUEST)
                user = User(first_name=first_name , last_name=last_name , email=email)
                user.set_password(password)
                user.save() 
            if user.is_parent == True or user.is_management == True :
                user.is_parent = True
                user.save()
                user.school.add(school)
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED )
            else:
                user.is_parent = True
                user.save()
                user.school.add(school)
                serializer = self.get_serializer(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED )

        return Response({'error': 'No referrer found'}, status=status.HTTP_400_BAD_REQUEST)








"""
    This view return the list of parent on the a specific school
"""
class SchoolParentRetrieve(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ParentRetrieveUpdateSerializer
    lookup_field = 'identifier'

    def get(self, request,school_identifier , identifier , *args, **kwargs):
        print(request.data)
        try:
            school = School.objects.get(identifier=school_identifier)
        except School.DoesNotExist:
            return Response({'error' : 'School does not exist' } , status=status.HTTP_400_BAD_REQUEST )
        if User.objects.filter(is_parent=True , identifier=identifier).exists() :
            parent = User.objects.filter(is_parent=True , identifier=identifier ).first()
            serializer = self.get_serializer(parent)
            return Response(serializer.data , status=status.HTTP_200_OK )

        # try:
        #     parent = User.objects.filter(identifier="'")
        return super().get(request, *args, **kwargs) 



class ParentsCreateApiView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ParentRetrieveUpdateSerializer
    # def get(self , request , *args , **kwargs ):
    #     models = self.get_queryset()
    #     serializer = self.serializer_class(models , many=True)
    #     return Response(serializer.data)

    def post(self , request , identifier ,*args, **kwargs ):
        school_identifier = identifier
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            try:
                school = School.objects.get(identifier=school_identifier)
            except School.DoesNotExist : 
                return Response({'error' : 'school does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=serializer.validated_data['email'], is_parent=True).exits():
                user = User.objects.get(email=serializer.validated_data['email'])
                user.schools.add(school)
            else:
                user = User()
                return Response({'error' : 'user does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            user_serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


