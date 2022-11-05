from django.urls import path
from . import views

 

urlpatterns = [ 
    path('auth/register/parent', views.ParentRegisterApiView.as_view(), name='parent-register'),
    path('auth/register/schooladmin', views.SchoolAdminRegisterApiView.as_view(), name='school-admin-register'),
    path('auth/login', views.LoginApiView.as_view(), name='login'),

    path('schools/<str:identifier>/join', views.ParentSchoolJoinApiView.as_view()),
    

    path('password/forget', views.ResetPasswordRequestEmailApiView.as_view(), name='password_reset_request_email'),
    path('password/<str:token>/<str:uuidb64>/reset', views.SetNewPasswordTokenCheckApi.as_view(), name='password_reset_done'),
    path('password/reset', views.ChangePasswordView.as_view(), name='password_change'),

    path('schools', views.SchoolListCreateApiView.as_view()),
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