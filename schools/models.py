from django.db import models
# from accounts.models import Student
# from django.contrib.auth import get_user_model
# Create your models here.
# User = get_user_model() 


class School(models.Model):
    name = models.CharField(max_length=1000)
    company_name = models.TextField(null=True , blank=True )
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    rc_number = models.PositiveIntegerField(null=True , blank=True )
    identifier = models.CharField(max_length=15, null=True , blank=True ,  unique=True)
    address = models.TextField()
    cac_verified = models.BooleanField(default=False)
    # email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self) -> str:
        return self.name

    
    





