from django.db import models
from django.contrib.auth.models import AbstractBaseUser , PermissionsMixin ,BaseUserManager
# Create your models here.





def upload_to(instance, filename):
    return 'profiles/{filename}'.format(filename=filename)


class UserManager(BaseUserManager):

    def create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model( email=email , **extra_fields)
        user.set_password(password)
        user.save()
        return user
    

    def create_superuser(self,email,password, **extra_fields):

        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('superuser must be given is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('superuser must be given is_superuser=True')
        return self.create_user(email,password,**extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    GENDER_STATUS = (
        ('male', 'male'),
        ('female','female'),
    )
    identifier = models.CharField(max_length=100, null=True , blank=True , unique=True )
    first_name = models.CharField(max_length=100, null=True , blank=True)
    last_name = models.CharField(max_length=100 , null=True , blank=True) 
    gender = models.CharField(max_length=10 , choices=GENDER_STATUS , null=True , blank=True) 
    email = models.EmailField(unique=True)
    image = models.ImageField(default='profiles/image-default.png', upload_to=upload_to , null=True , blank=True)
    address = models.TextField(null=True , blank=True)
    phone_number = models.CharField(max_length=20 , null=True , blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    objects= UserManager()

    USERNAME_FIELD ="email"
    # REQUIRED_FIELDS = ['first_name']




    def __str__(self):
        return self.email
    



class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100 , null=True , blank=True)
    identifier = models.CharField(max_length=100, null=True , blank=True  , unique=True )
    parent = models.ForeignKey( 'accounts.ChannelUser', on_delete=models.SET_NULL , null=True , blank=True) 
    channel = models.ForeignKey('schools.Channel', on_delete=models.CASCADE, null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 


 

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class AccountActivation(models.Model):
    email = models.EmailField()
    active_token = models.CharField(max_length=1000)


class AccountActivationCode(models.Model):
    email = models.EmailField()
    code = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)




class ChannelUser(models.Model):
    identifier = models.CharField(max_length=17 , null=True , blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True , blank=True)
    first_name = models.CharField(max_length=100, null=True , blank=True)
    last_name = models.CharField(max_length=100 , null=True , blank=True) 
    email = models.EmailField()
    channel = models.ForeignKey('schools.Channel', on_delete=models.CASCADE, null=True , blank=True)
    # the admin  is the user that created the channel 
    is_parent = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.first_name 