import random
import string
from threading import Thread
from .signals import random_string_generator_user
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes,   force_str, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import generics, status
from rest_framework.decorators import permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

from .mail_services import MailServices
from .models import AccountActivation, AccountActivationCode, Student, User
from .serializers import (
    ChangePasswordSerializer, ClientRegisterSerializer, 
    LoginSerializer, ResetPasswordRequestEmailSerializer,
    SetNewPasswordSerializer, UserProfileImageSerializer, 
    UserAccountActivationCodeConfirmSerializer, UserVettingSerializer,
    UserEmailPremblyConfirmSerializer, UserSerializer)
from .tokens import create_jwt_pair_for_user
from .utils import PremblyServices


class ResetPasswordRequestEmailApiView(generics.GenericAPIView):
    serializer_class = ResetPasswordRequestEmailSerializer
 
    @swagger_auto_schema(
        operation_description='Request a password reset',
        operation_summary='Request password reset'
    )
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
                        {'success':True , 'detail': 'Password reset instruction will be sent to the mail' },
                        status=status.HTTP_200_OK
                        )
            except:
                return Response( 
                    {'success':True , 'detail': 'Password reset mail sent' }, 
                    status=status.HTTP_200_OK
                    )
        return Response( 
                    {'success':False , 'detail': 'Enter a valid email address' }, 
                    status=status.HTTP_400_BAD_REQUEST
                    )

# This view handle changing of user password on forget password
class SetNewPasswordTokenCheckApi(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    @swagger_auto_schema(
        operation_description='Reset password confirm',
        operation_summary='Reset password confirm'
    )
    def post(self, request, token , uuidb64 ):
        try:
            id = smart_str(urlsafe_base64_decode(uuidb64))
            user = User.objects.get(id=id)
            password1 = request.data['password1']
            password2 = request.data['password2']
            if password1 != password2 :
                return  Response({'success':False ,'detail': 'Password does not match'} , status=status.HTTP_400_BAD_REQUEST)
            if PasswordResetTokenGenerator().check_token(user, token):
                data = request.data
                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
                user.set_password(serializer.validated_data['password1'])
                user.save() 
                return Response({'success':True , 'detail':'Password updated successfully'}, status=status.HTTP_200_OK)
            return Response({'success':False ,'detail':'Token is not valid'}, status=status.HTTP_400_BAD_REQUEST)
        except DjangoUnicodeDecodeError as identifier:
            return Response({'success':False ,'detail': 'Token is not valid'}, status=status.HTTP_400_BAD_REQUEST)


#  This view handle password update within app ( authenticated user)
class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [ IsAuthenticated ] 
    model = User

    def get_object(self,queryset=None):
        obj = self.request.user
        return obj
    
    @swagger_auto_schema(
        operation_description='Change password',
        operation_summary='Change password'
    )
    def post(self, request, *args, **kwargs):
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
                return  Response({'success':False ,'detail': 'Password does not match'} , status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            """
                check if the user as already register but have not verify his or her account yet
                !!! CHECK IF THE CREATED AT IS MORE THAN 24 HOURS
            """
            attempted_user = User.objects.filter(email=email , is_verified=False, )
            if attempted_user.exists():
                user = attempted_user.first()
                user.set_password(password2)
                user.is_active = False
                user.save()
                return Response( { 
                    'success': True , 
                    'detail' :'Account activation code as been sent to your email',
                    'email': user.email
                    }, status=status.HTTP_201_CREATED  )
            return Response({'success': False , 'detail':'Email already exist'}, status=status.HTTP_400_BAD_REQUEST)
        # At this point we can now call the prembly APi to verify the email
        verify = True
        if verify :
            code = ''.join(random.choice(string.digits) for _ in range(4))
            AccountActivationCode.objects.create(email=email, code=int(code))
            Thread(target=MailServices.user_register_verification_email, kwargs={
                        'email': email , 'code' : code
                    }).start()
            user = User.objects.create(email=email)
            user.identifier =  random_string_generator_user()
            user.set_password(password2)
            user.is_active = False
            user.save()
            return Response( { 
                'success': True , 
                'detail' :'Account activation code as been sent to your email',
                'email': user.email
                }, status=status.HTTP_201_CREATED  )
        return Response({'success':False , 'detail':'Invalid email address'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserAccountActivationCodeConfirmApiView(generics.GenericAPIView):
    serializer_class = UserAccountActivationCodeConfirmSerializer

    """
    Activate user account using the code sent to the user email
    """

    @swagger_auto_schema(
        operation_description='Activate user account with the activation code',
        operation_summary='Activate user account'
    )
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

    @swagger_auto_schema(
        operation_summary='Complete user profile'
    )
    def post(self, request:Response ):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True) :
            first_name = serializer.validated_data.get('first_name',None)
            last_name = serializer.validated_data.get('last_name', None)
            phone_number = serializer.validated_data.get('phone_number', None)     
            gender = serializer.validated_data.get('gender', None)
            try:
                user = User.objects.get(id=request.user.id)
            except:
                return Response({'success':False ,'detail': 'User does not exits'} , status=status.HTTP_404_NOT_FOUND)
            if first_name != None:
                user.first_name = first_name
            if last_name is not None :
                user.last_name = last_name
            if phone_number is not None:
                user.phone_number = phone_number
            if gender is not None :
                user.gender = gender.lower()
            user.is_active = True
            user.save()
            serializer = UserSerializer(user)
            return Response({'success':True , 'detail': 'Profile successfully updated', 'user': serializer.data},status.HTTP_200_OK)


class UserProfileImageUploadApiView(generics.GenericAPIView):
        serializer_class = UserProfileImageSerializer
        queryset = User.objects.all()
        parser_classes =[ MultiPartParser]
        # permission_classes = [ IsAuthenticated ] 
        

        @swagger_auto_schema(
            operation_description='Upload user profile image',
            operation_summary='User profile image upload endpoint'
        )
        def post(self, request ):
            data = request.data
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(id=request.user.id)
            user.image = serializer.validated_data['image']
            user.save() 
            return Response(status=status.HTTP_200_OK)



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
                return  Response({'success':False ,'detail': 'Password does not match'} , status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(email=email)
                return Response({'success':False ,'detail': 'Email already exists'} , status=status.HTTP_400_BAD_REQUEST)
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
            return Response({'success':True , 'detail': 'Verification mail as been sent to the email address'},status.HTTP_200_OK)


class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_summary='Authenticate user'
    )
    def post(self, request ):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email , password=password)
            if user is not None :
                if user.is_verified == False :
                    return Response(
                        {
                            'success':False, 
                            'detail':'You have not verify your account, kindly register again'
                        },
                            status=status.HTTP_401_UNAUTHORIZED
                        )
                serializer = UserSerializer(user)
                tokens = create_jwt_pair_for_user(user)
                response = {
                    'success': True ,
                    'detail': 'Login is successful',
                    "tokens" : tokens , 
                    'user' : serializer.data 
                }
                return Response(response , status=status.HTTP_200_OK)
            
            return Response({'success': False , 'detail': 'Invalid login credential'}, status=status.HTTP_400_BAD_REQUEST)



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
          
        return Response({'success':False , 'detail': 'Mail verification is invalid'},status.HTTP_200_OK)






email_vetting_response = {
    "status": True,
    "response_code": "00",
    "message": "Successful",
    "data": {
        "basic": {
            "smtp-status": "ok",
            "domain-error": False ,
            "verified": True,
            "is-freemail": True,
            "is-disposable": False ,
            "valid": True,
            "is-catch-all": False ,
            "is-deferred": False ,
            "provider": "gmail.com",
            "domain": "gmail.com",
            "smtp-response": "250 2.1.5 OK oz43-20020a1709077dab00b0072ac7a2726esi1583583ejc.474 - gsmtp",
            "syntax-error": False ,
            "email": "user@gmail.com",
            "is-personal": True
        },
        "other": {
            "email": "user@gmail.com",
            "reputation": "high",
            "suspicious": False ,
            "references": 5,
            "details": {
                "blacklisted": False ,
                "malicious_activity": False ,
                "malicious_activity_recent": False ,
                "credentials_leaked": True,
                "credentials_leaked_recent": False ,
                "data_breach": True,
                "first_seen": "05/24/2019",
                "last_seen": "10/03/2020",
                "domain_exists": True,
                "domain_reputation": "n/a",
                "new_domain": False ,
                "days_since_domain_creation": 9824,
                "suspicious_tld": False,
                "spam": False,
                "free_provider": True,
                "disposable": False,
                "deliverable": True,
                "accept_all": False,
                "valid_mx": True,
                "primary_mx": "gmail-smtp-in.l.google.com",
                "spoofable": True,
                "spf_strict": True,
                "dmarc_enforced": False,
                "profiles": [
                    "twitter",
                    "gravatar"
                ]
            }
        },
        "domain_info": {
            "domain_name": "GMAIL.COM",
            "registry_domain_id": "4667231_DOMAIN_COM-VRSN",
            "registrar_whois_server": "whois.markmonitor.com",
            "registrar_url": "http",
            "updated_date": "2021-07-11T09",
            "creation_date": "1995-08-13T04",
            "registry_expiry_date": "2022-08-12T04",
            "registrar": "MarkMonitor Inc.",
            "registrar_iana_id": "292",
            "registrar_abuse_contact_email": "abusecomplaints@markmonitor.com",
            "registrar_abuse_contact_phone": "+1.2086851750",
            "domain_status": "serverUpdateProhibited https",
            "name_server": "NS4.GOOGLE.COM",
            "dnssec": "unsigned",
            "url_of_the_icann_whois_inaccuracy_complaint_form": "https",
            "last_update_of_whois_database": "2022-07-07T08"
        },
        "breaches": [
            {
                "Name": "Appen",
                "Title": "Appen",
                "Domain": "appen.com",
                "BreachDate": "2020-06-22",
                "AddedDate": "2020-07-30T07:00:21Z",
                "ModifiedDate": "2020-07-30T07:00:21Z",
                "PwnCount": 5888405,
                "Description": "In June 2020, the AI training data company <a href=\"https://www.bleepingcomputer.com/news/security/hacker-leaks-386-million-user-records-from-18-companies-for-free/\" target=\"_blank\" rel=\"noopener\">Appen suffered a data breach</a> exposing the details of almost 5.9 million users which were subsequently sold online. Included in the breach were names, email addresses and passwords stored as bcrypt hashes. Some records also contained phone numbers, employers and IP addresses. The data was provided to HIBP by <a href=\"https://dehashed.com/\" target=\"_blank\" rel=\"noopener\">dehashed.com</a>.",
                "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/Appen.png",
                "DataClasses": [
                    "Email addresses",
                    "Employers",
                    "IP addresses",
                    "Names",
                    "Passwords",
                    "Phone numbers"
                ],
                "IsVerified": True,
                "IsFabricated": False,
                "IsSensitive": False,
                "IsRetired": False,
                "IsSpamList": False,
                "IsMalware": False
            },
            {
                "Name": "Canva",
                "Title": "Canva",
                "Domain": "canva.com",
                "BreachDate": "2019-05-24",
                "AddedDate": "2019-08-09T14:24:01Z",
                "ModifiedDate": "2019-08-09T14:24:01Z",
                "PwnCount": 137272116,
                "Description": "In May 2019, the graphic design tool website <a href=\"https://support.canva.com/contact/customer-support/may-24-security-incident-faqs/\" target=\"_blank\" rel=\"noopener\">Canva suffered a data breach</a> that impacted 137 million subscribers. The exposed data included email addresses, usernames, names, cities of residence and passwords stored as bcrypt hashes for users not using social logins. The data was provided to HIBP by a source who requested it be attributed to \"JimScott.Sec@protonmail.com\".",
                "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/Canva.png",
                "DataClasses": [
                    "Email addresses",
                    "Geographic locations",
                    "Names",
                    "Passwords",
                    "Usernames"
                ],
                "IsVerified": True,
                "IsFabricated": False,
                "IsSensitive": False,
                "IsRetired": False,
                "IsSpamList": False,
                "IsMalware": False
            },
            {
                "Name": "Gravatar",
                "Title": "Gravatar",
                "Domain": "gravatar.com",
                "BreachDate": "2020-10-03",
                "AddedDate": "2021-12-05T22:45:58Z",
                "ModifiedDate": "2021-12-08T01:47:02Z",
                "PwnCount": 113990759,
                "Description": "In October 2020, <a href=\"https://www.bleepingcomputer.com/news/security/online-avatar-service-gravatar-allows-mass-collection-of-user-info/\" target=\"_blank\" rel=\"noopener\">a security researcher published a technique for scraping large volumes of data from Gravatar, the service for providing globally unique avatars </a>. 167 million names, usernames and MD5 hashes of email addresses used to reference users' avatars were subsequently scraped and distributed within the hacking community. 114 million of the MD5 hashes were cracked and distributed alongside the source hash, thus disclosing the original email address and accompanying data. Following the impacted email addresses being searchable in HIBP, <a href=\"https://en.gravatar.com/support/data-privacy\" target=\"_blank\" rel=\"noopener\">Gravatar release an FAQ detailing the incident</a>.",
                "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/Gravatar.png",
                "DataClasses": [
                    "Email addresses",
                    "Names",
                    "Usernames"
                ],
                "IsVerified": True,
                "IsFabricated": False,
                "IsSensitive": False,
                "IsRetired": False,
                "IsSpamList": False,
                "IsMalware": False
            }
        ],
        "identitypass_verification": {
            "status": False,
            "response_code": "05",
            "message": "Endpoint has been disable or inactive...please contact administrator"
        },
        "kyc": {},
        "instagram": {
            "active": True,
            "data": {}
        },
        "pinterest": {
            "active": True,
            "data": {}
        },
        "twitter": {
            "active": True,
            "data": {}
        },
        "gravatar": {
            "active": True,
            "data": {
                "entry": [
                    {
                        "id": "117899327",
                        "hash": "dc37423cea1ea33099a1667a2bc4550f",
                        "requestHash": "dc37423cea1ea33099a1667a2bc4550f",
                        "profileUrl": "http://gravatar.com/rugipo",
                        "preferredUsername": "rugipo",
                        "thumbnailUrl": "https://secure.gravatar.com/avatar/dc37423cea1ea33099a1667a2bc4550f",
                        "photos": [
                            {
                                "value": "https://secure.gravatar.com/avatar/dc37423cea1ea33099a1667a2bc4550f",
                                "type": "thumbnail"
                            }
                        ],
                        "name": {
                            "givenName": "Name",
                            "familyName": "Surname",
                            "formatted": "Full Name"
                        },
                        "displayName": "codeAdept",
                        "urls": []
                    }
                ]
            }
        },
        "github": {
            "active": False,
            "data": {}
        },
        "discord": {
            "active": True,
            "data": {}
        },
        "ebay": {
            "active": False,
            "data": {}
        },
        "linkedin": {
            "active": True,
            "data": {}
        }
    }
}





phone_vetting_response = {
    "status": True,
    "response_code": "00",
    "message": "Successful",
    "data": {
        "basic": {
            "valid": True,
            "number": "2348030000000",
            "local_format": "08030000000",
            "international_format": "+2348030000000",
            "country_prefix": "+234",
            "country_code": "NG",
            "country_name": "Nigeria (Federal Republic of)",
            "location": "",
            "carrier": "MTN Nigeria Communications Ltd",
            "line_type": "mobile"
        },
        "socials": [
            "facebook.com",
            "twitter.com",
            "linkedin.com",
            "instagram.com",
            "vk.com"
        ],
        "other_social_media": {
            "is_registered": True,
            "profile_picture": "",
            "contact_info": {
                "businessProfile": {
                    "id": {
                        "server": "c.us",
                        "user": "2348030000000",
                        "_serialized": "2348030000000@c.us"
                    },
                    "tag": "4107712435",
                    "description": "I solve problems with Python and Javascript.\nI am your favourite software engineer👨🏻‍💻",
                    "categories": [
                        {
                            "id": "176831012360626",
                            "localized_display_name": "Professional Service"
                        }
                    ],
                    "profileOptions": {
                        "commerceExperience": "none",
                        "cartEnabled": True
                    },
                    "email": "email@email.com",
                    "website": [
                        "https://sitelink.com"
                    ],
                    "latitude": 6.5244,
                    "longitude": 3.3792,
                    "businessHours": {
                        "config": {
                            "sun": {
                                "mode": "open_24h"
                            },
                            "mon": {
                                "mode": "open_24h"
                            },
                            "tue": {
                                "mode": "open_24h"
                            },
                            "wed": {
                                "mode": "open_24h"
                            },
                            "thu": {
                                "mode": "open_24h"
                            },
                            "fri": {
                                "mode": "open_24h"
                            },
                            "sat": {
                                "mode": "open_24h"
                            }
                        },
                        "timezone": "Africa/Lagos"
                    },
                    "address": "Lagos, Nigeria",
                    "fbPage": {},
                    "igProfessional": {},
                    "isProfileLinked": False,
                    "customUrlPaths": [],
                    "coverPhoto": None
                },
                "id": {
                    "server": "c.us",
                    "user": "23480",
                    "_serialized": "2348030000000@c.us"
                },
                "number": "2348030000000",
                "isBusiness": True,
                "isEnterprise": False,
                "labels": [],
                "pushname": "Segun Isreal A.",
                "type": "in",
                "verifiedLevel": 0,
                "verifiedName": "Segun Isreal A.",
                "isMe": True,
                "isUser": True,
                "isGroup": False,
                "isWAContact": True,
                "isMyContact": False,
                "isBlocked": False
            }
        }
    }
}




class UserVettingApiView(generics.GenericAPIView):
    serializer_class =  UserVettingSerializer


    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        response = email_vetting_response
        response_phone = phone_vetting_response
        # print(response)
#   "email": "user@gmail.com",
#             "reputation": "high", malicious_activity
#             "suspicious": False ,
        response_data = {'success':True , 'detail':'Verification successful'}
        
        if response_phone['response_code'] == '00' :
            if response_phone['data']['basic']['valid']:
                response_data.update({
                    "valid": True,
                    "number": "2348030000000",
                    "country_prefix": "+234",
                    "country_code": "NG",
                    "country_name": "Nigeria (Federal Republic of)",
                    "carrier": "MTN Nigeria Communications Ltd",
                    "line_type": "mobile",
                    "verifiedName": "Segun Isreal A.",
                    "socials": [
                    "facebook.com",
                    "twitter.com",
                    "linkedin.com",
                    "instagram.com",
                    "vk.com"
                    ]
                })
        
        if response['response_code'] == '00' :          
            response_data.update({'reputation': 'High'}) if response['data']['other']['reputation'] == 'high' else response_data.update({ 'reputation': 'Low'})
            response_data.update({'suspicious': 'User is suspicious'}) if response['data']['other']['suspicious'] else response_data.update({'suspicious': 'User not suspicious'})

            if response['data']['other']['details']['malicious_activity'] == True:
                response_data.update({'malicious_activity' : 'Malicious activity found' })
            else:
                response_data.update({  'malicious_activity' : 'Malicious activity not found' })

            return Response(response_data , status=status.HTTP_200_OK)
        

        return Response({'success': False , 'detail':'Record not found'} , status=status.HTTP_404_NOT_FOUND)