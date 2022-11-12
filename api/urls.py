from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
 

urlpatterns = [ 

    path('auth/register', views.UserRegisterWithPremblyEmailConfirmApiView.as_view(), name='register'),
    path('auth/profile/complete', views.UserProfileUpdateApiView.as_view(), name='register-profile'),
    path('auth/register/verify', views.UserAccountActivationCodeConfirmApiView.as_view(), name='code-confirm'),
    path('auth/token',views.LoginApiView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/password/reset', views.ResetPasswordRequestEmailApiView.as_view(), name='password_reset_request_email'),
    path('auth/password/<str:token>/<str:uuidb64>/reset', views.SetNewPasswordTokenCheckApi.as_view(), name='password_reset_done'),
    path('auth/password/change', views.ChangePasswordView.as_view(), name='password_change'),



    path('channels', views.ChannelsListCreateApiView.as_view() , name='list-create-channel'),
    path('channels/verify', views.ChannelActivationCodeConfirmApiView.as_view() , name='channel-code-verify'),
    path('channels/users/join', views.ChannelUserJoinApiView.as_view(), name='join-channel'), 
    path('channels/<str:identifier>', views.ChannelsRetrieveUpdateDestroyApiView.as_view(), name='retrieve-update-destroy-channel'),
    path('channels/<str:identifier>/students', views.ChannelStudentListCreateApiView.as_view(), name='list-create-channel-students'),
    path('channels/<str:identifier>/students/verify', views.ChannelVerifiedPickedStudentsAPIView.as_view(), name='list-channel-students-verify'),
    path('channels/<str:identifier>/students/upload', views.ChannelStudentUploadCsvApiView.as_view(), name='channel-students-upload'),
    path('channels/<str:identifier>/parents', views.ChannelParentsListCreateAPIView.as_view(), name='list-create-channel-parents'),
    path('channels/<str:identifier>/parents/upload', views.ChannelUserUploadCsvApiView.as_view(), name='channel-users-upload'),



    path('channels/<str:channel_identifier>/parents/<str:channel_user_identifier>/map', views.MapStudentsToParentApiView.as_view(), name='list-channel-user-kids'), 
    # path('channels/<str:channel_identifier>/kids', views.ChannelParentKidsListAPIView.as_view() , name='parent-retrieve-kid-list'),
    # path('channels/<str:channel_identifier>/users/<str:channel_user_identifier>', views.ChannelUsersRetrieveUpdateDestroyAPIView.as_view(), name='retrieve-update-destroy-channeluser'),
    

    path('students/<str:identifier>', views.StudentRetrieveUpdateDestroyAPIView.as_view(), name='retrieve-update-student'),
    path('students/<str:identifier>/verify', views.StudentPickUpVerificationApiView.as_view(), name='verify-student-picked'),
    path('students/<str:identifier>/history', views.StudentPickUpVerificationHistoryApiView.as_view(), name='retrieve-student-verification-history'), 



] 