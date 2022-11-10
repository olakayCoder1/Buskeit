from django.db import models
from schools.models import Channel
# Create your models here.



class PaymentTransaction(models.Model):
    TRANSACTION_STATUS = (
        ('pending', 'pending'),
        ('success','success'),
        ('failed','failed'),
    )
    channel = models.ForeignKey(Channel , on_delete=models.SET_NULL , null=True)
    amount = models.DecimalField(max_digits=100, null=True , decimal_places=2)
    status = models.CharField(max_length=10, default='pending' , choices=TRANSACTION_STATUS)
    payment_reference = models.CharField(max_length=100, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f'{self.channel.name} , {self.amount} , {self.status}'