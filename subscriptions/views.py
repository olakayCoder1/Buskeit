import requests

from django.shortcuts import render
from django.conf import settings

from .models import PaymentTransaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics , status
from accounts.models import ChannelUser 
# Create your views here.

def index(request):
    user = ChannelUser.objects.get(id=30)
    print(user.__class__) 
    m  = user.__class__.objects.all()
    for k in m:
        print(k.first_name) 

    if request.method == 'POST':
        print('Yes')
        email = request.POST.get('email')
        amount = int(request.POST.get('amount'))
        # return render(request, 'subscriptions/confirm.html')
    return render(request , 'subscriptions/payment.html')


class ConfirmPaymentApiView(APIView):
    def get(self, request , payment_reference):
        reference = payment_reference
        url = f'https://api.paystack.co/transaction/verify/reference=386089469'
        # url = f'https://api.paystack.co/transaction/verify/:{reference}'
        header = {
            { 'authorization': f'Bearer sk_test_f2c4c12c87df60bc178d3be7a19ba4a975d17527' } 

        }
        response = requests.get(url, headers=header)
        print(response.status_code)
        return Response({'status': 'ok' },status=status.HTTP_200_OK) 




class PaymentTransactionApiView(APIView):
    def get(self,request , reference):
        payment = PaymentTransaction.objects.get( payment_reference=reference , book__user__id=request.user.id )
        reference = payment.payment_reference
        url = 'https://api.paystack.co/transaction/verify/{}'.format(reference)
        paystack_key = settings.PAYSTACK_SECRET_KEY
        headers = {
            {'authorization': f'Bearer { paystack_key }' }
        }
        r = requests.get(url , headers=headers)
        response = r.json()
        if response['data']['status'] == 'success':
            amount = response['data']['amount'] 
            payment.status = 'success'
            payment.amount = amount
            payment.save()
            return Response(response)
        return Response(response)