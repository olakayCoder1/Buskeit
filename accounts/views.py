import random
import string
from threading import Thread

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (DjangoUnicodeDecodeError, force_bytes,
                                   force_str, smart_str)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.decorators import permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from .mail_services import MailServices
from .models import AccountActivation, AccountActivationCode, Student, User
from .serializers import (ChangePasswordSerializer, ClientRegisterSerializer,
                          LoginSerializer, ResetPasswordRequestEmailSerializer,
                          SetNewPasswordSerializer,
                          UserAccountActivationCodeConfirmSerializer,
                          UserEmailPremblyConfirmSerializer, UserSerializer)
from .tokens import create_jwt_pair_for_user
from .utils import PremblyServices


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
                Thread(target=MailServices.forget_password_mail, kwargs={
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
            password1 = request.data['password1']
            password2 = request.data['password2']
            if password1 != password2 :
                return  Response({'success':False ,'message': 'Password does not match'} , status=status.HTTP_400_BAD_REQUEST)
            if PasswordResetTokenGenerator().check_token(user, token):
                data = request.data
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                user.set_password(serializer.validated_data['password1'])
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
            password1 = serializer.validated_data['password1']
            password2 = serializer.validated_data['password2']
            if password1 != password2 :
                return  Response({'success':False ,'detail': 'Password does not match'} , status=status.HTTP_400_BAD_REQUEST)
            if not self.object.check_password(serializer.data.get('old_password')):
                return Response({'success':False ,'detail': 'wrong password'}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("password2"))
            self.object.save()
            response={
                'success': True,
                'detail': 'Password updated successfully',
                }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterWithPremblyEmailConfirmApiView(generics.GenericAPIView):
    serializer_class = UserEmailPremblyConfirmSerializer

    @swagger_auto_schema(
        operation_description="This endpoint handle the creation of user",
        operation_summary="Register new user"
    )
    def post(self, request) :
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password1 = serializer.validated_data['password1']
        password2 = serializer.validated_data['password2']
        if password1 != password2 :
                return  Response({'success':False ,'message': 'Password does not match'} , status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'success': False , 'detail':'Email already exist'}, status=status.HTTP_400_BAD_REQUEST)
        # At this point we can now call the prembly APi to verify the email
        verify = True
        # verify = PremblyServices.user_signup_verification_mail(email=email)
        if verify :
            code = ''.join(random.choice(string.digits) for _ in range(4))
            AccountActivationCode.objects.create(email=email, code=int(code))
            Thread(target=MailServices.user_register_verification_email, kwargs={
                        'email': email , 'code' : code
                    }).start()
            user = User.objects.create(email=email)
            user.set_password(password2)
            user.is_active = False
            user.save()
            return Response( { 
                'success': True , 
                'detail' :'Account activation code as been sent to your email',
                'email': user.email
                }, status=status.HTTP_200_OK  )
        return Response({'success':False , 'detail':'Invalid email address'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserAccountActivationCodeConfirmApiView(generics.GenericAPIView):
    serializer_class = UserAccountActivationCodeConfirmSerializer
    def post(self, request) :
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        is_code_valid = AccountActivationCode.objects.filter(email=email, code=int(code))
        if is_code_valid:
            user = User.objects.get(email=email)
            user.is_active = True
            user.is_verified = True
            user.save()
            is_code_valid.first().delete()
            serializer = UserSerializer(user)
            tokens = create_jwt_pair_for_user(user)
            response = {
                'success': True ,
                'detail': 'Account activated successfully',
                "tokens" : tokens , 
                'user' : serializer.data 
            }
            return Response(response , status=status.HTTP_200_OK)


#  authentication views starts
class UserProfileUpdateApiView(generics.GenericAPIView):
    """
    This view is used in the registration of a new user
    """
    serializer_class = ClientRegisterSerializer
    permission_classes = [ IsAuthenticated ]

    def post(self, request:Response ):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True) :
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            phone_number = serializer.validated_data['phone_number']
            gender = serializer.validated_data['gender']
            try:
                user = User.objects.get(id=request.user.id)
            except:
                return Response({'success':False ,'detail': 'Email already exists'} , status=status.HTTP_400_BAD_REQUEST)
            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = phone_number
            user.gender = gender
            user.is_active = True
            user.save()
            serializer = UserSerializer(user)
            return Response({'success':True , 'detail': 'Profile successfully updated', 'user': serializer.data},status.HTTP_200_OK)



class ParentRegisterApiView(generics.GenericAPIView):
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
                Thread(target=MailServices.account_activation_mail, kwargs={
                        'email': user.email ,'token': token , 'uuidb64':uuidb64
                    }).start()
                AccountActivation.objects.create(active_token=token , email=user.email)
            return Response({'success':True , 'message': 'Verification mail as been sent to the email address'},status.HTTP_200_OK)


class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request ):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email , password=password)
            if user is not None :
                serializer = UserSerializer(user)
                tokens = create_jwt_pair_for_user(user)
                response = {
                    'success': True ,
                    'message': 'Login is successful',
                    "tokens" : tokens , 
                    'user' : serializer.data 
                }
                return Response(response , status=status.HTTP_200_OK)
            
            return Response({'success': False , 'message': 'Invalid login credential'}, status=status.HTTP_200_OK)



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




