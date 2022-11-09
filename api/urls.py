from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
 

urlpatterns = [ 

    path('auth/register', views.UserRegisterApiView.as_view(), name='register'),
    # path('auth/register/parent', views.ParentRegisterApiView.as_view(), name='parent-register'),
    # path('auth/register/schooladmin', views.SchoolAdminRegisterApiView.as_view(), name='school-admin-register'),
    path('auth/token',views.LoginApiView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/password/reset', views.ResetPasswordRequestEmailApiView.as_view(), name='password_reset_request_email'),
    path('auth/password/<str:token>/<str:uuidb64>/reset', views.SetNewPasswordTokenCheckApi.as_view(), name='password_reset_done'),
    path('auth/password/change', views.ChangePasswordView.as_view(), name='password_change'),
 

    path('channels', views.ChannelsListCreateApiView.as_view()),
    path('channels/<str:identifier>', views.ChannelsRetrieveUpdateDestroyApiView.as_view()),
    path('channels/<str:invitation_code>/join', views.ChannelUserJoinApiView.as_view()), 
    path('channels/<str:school_identifier>/students', views.ChannelStudentListCreateApiView.as_view()),
    path('channels/<str:school_identifier>/users', views.ChannelUsersListAPIView.as_view()),
    path('channels/<str:school_identifier>/kids', views.ChannelParentKidsListAPIView.as_view()),
    path('channels/<str:school_identifier>/users/<str:channel_user_identifier>', views.ChannelUsersRetrieveUpdateDestroyAPIView.as_view()),


    path('students/<str:identifier>', views.StudentRetrieveUpdateDestroyAPIView.as_view()),
    path('students/<str:identifier>/verify', views.StudentPickUpVerificationApiView.as_view()),
    path('students/<str:identifier>/history', views.StudentPickUpVerificationHistoryApiView.as_view()), 




    






    path('schools', views.SchoolListCreateApiView.as_view()),
    path('schools/<str:identifier>/join', views.ParentSchoolJoinApiView.as_view()),
    path('schools/<str:identifier>', views.SchoolRetrieveUpdateDestroyApiView.as_view()),
    path('schools/<str:school_identifier>/parents', views.SchoolParentListCreateAPIView.as_view()),
    path('schools/<str:school_identifier>/parents/<str:parent_id>', views.SchoolParentListCreateAPIView.as_view()),
    path('schools/<str:school_identifier>/students', views.SchoolStudentsListCreateAPIView.as_view()),
    path('schools/<str:school_identifier>/students/<str:student_identifier>', views.SchoolStudentRetrieveDestroyAPIView.as_view()),


    path('schools/<str:school_identifier>/parents/<str:identifier>', views.SchoolParentRetrieveUpdateAPIView.as_view()),





    # path('parents', views.ParentUsersListCreateApiView.as_view()),
    # path('parents/<str:identifier>', views.ParentRetrieveUpdateAPIView.as_view()),
    # path('parents/<str:school_identifier>/parents', views.SchoolParentListCreateAPIView.as_view()),
    # path('schools/<str:school_identifier>/parents/<str:identifier>', views.ParentRetrieveUpdateAPIView.as_view()),
    # path('schools/<str:identifier>/parents/register', views.ParentsCreateApiView.as_view()),
] 