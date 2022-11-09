from django.db import models
# from accounts.models import Student
# from django.contrib.auth import get_user_model
# Create your models here.
# User = get_user_model() 

def upload_to(instance, filename):
    return 'channels/{filename}'.format(filename=filename)

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

    

class Channel(models.Model):
    identifier = models.CharField(max_length=15, null=True , blank=True ,  unique=True)
    name = models.CharField(max_length=1000)
    company_name = models.TextField(null=True , blank=True )
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    rc_number = models.PositiveIntegerField(null=True , blank=True )
    address = models.TextField()
    invitation_code = models.CharField(max_length=15 , unique=True ,  blank=True ,  null=True )
    # image = models.ImageField(upload_to=upload_to , null=True , blank=True)
    cac_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    has_subscribed = models.BooleanField(default=False)



    def __str__(self) -> str:
        return self.name 



class StudentPickUpVerification(models.Model):
    student = models.ForeignKey('accounts.Student' , on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.student.first_name




