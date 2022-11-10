from rest_framework import serializers
from .models import PaymentTransaction
import environ
import requests
from django.conf import settings



env = environ.Env()
environ.Env.read_env()


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['id','channel','amount', 'payment_reference', 'status' ,'created_at', ]

    def save(self):
        url = 'https://api.paystack.co/tarnsaction/initialize'
        paystack_key = settings.PAYSTACK_SECRET_KEY
        header = {
            { 'authorization': f'Bearer  { paystack_key } ' } 

        }
        data = {
            'amount':self.validated_data['amount'],
            'email': self.context['request'].user.email
        }
        r = requests.post(url, headers=header , data=data)
        response = r.json()

        PaymentTransaction.objects.create(
            status = 'pending',
            book = self.validated_data['book'],
            amount = response['data']['amount'],
            payment_reference = response['data']['reference']
        )
        return response
