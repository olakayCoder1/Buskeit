from django.urls import path
from . import views




urlpatterns = [ 
    path('', views.index),
    path('verify/<str:payment_reference>', views.ConfirmPaymentApiView.as_view()),
]