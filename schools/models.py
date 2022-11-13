from django.db import models

def upload_to(instance, filename):
    return 'channels/{filename}'.format(filename=filename)


    

class Channel(models.Model):
    identifier = models.CharField(max_length=15, null=True , blank=True ,  unique=True)
    name = models.CharField(max_length=1000 )
    email = models.EmailField(null=True , blank=True)
    phone_number = models.CharField(max_length=20 , null=True , blank=True)
    rc_number = models.CharField(max_length=1000, null=True , blank=True )
    company_type = models.CharField(max_length=10 , null=True , blank=True )
    address = models.TextField(null=True, blank=True)
    invitation_code = models.CharField(max_length=11, unique=True ,  blank=True ,  null=True )
    image = models.ImageField(upload_to=upload_to , null=True , blank=True)
    cac_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    has_subscribed = models.BooleanField(default=False)
    subscription_valid_until = models.DateField(null=True, blank=True)



    def __str__(self) -> str:
        return self.name 


class ChannelActivationCode(models.Model):
    user = models.ForeignKey('accounts.User' , on_delete=models.CASCADE , null=True , blank=True)
    email = models.EmailField()
    code = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class StudentPickUpVerification(models.Model):
    student = models.ForeignKey('accounts.Student' , on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.student.first_name








