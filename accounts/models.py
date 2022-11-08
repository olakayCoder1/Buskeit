from django.db import models
from django.contrib.auth.models import AbstractBaseUser , PermissionsMixin ,BaseUserManager
from schools.models import School 
# Create your models here.





def upload_to(instance, filename):
    return 'profiles/{filename}'.format(filename=filename)


class UserManager(BaseUserManager):

    def create_user(self, first_name,email,password,**extra_fields):
        if not first_name:
            raise ValueError('Invalid first name')
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(first_name=first_name , email=email , **extra_fields)
        user.set_password(password)
        user.save()
        return user
    

    def create_superuser(self,first_name,email,password, **extra_fields):

        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('superuser must be given is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('superuser must be given is_superuser=True')
        return self.create_user(first_name,email,password,**extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    identifier = models.CharField(max_length=100, null=True , blank=True , unique=True )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True )
    # image = models.ImageField(default='profiles/image-default.png', upload_to=upload_to)
    address = models.TextField(null=True , blank=True)
    phone_number = models.CharField(max_length=20 , null=True , blank=True)
    nin_number = models.PositiveIntegerField(null=True , blank=True)
    is_verified = models.BooleanField(default=False)
    # is_parent = models.BooleanField(default=False)
    # is_school_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    objects= UserManager()

    USERNAME_FIELD ="email"
    REQUIRED_FIELDS = ['first_name']




    def __str__(self):
        return self.first_name
    

class SchoolAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20 , null=True , blank=True)
    nin_number = models.PositiveIntegerField(null=True , blank=True)
    is_owner = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  
    school = models.ManyToManyField('schools.School', related_name='admin_schools')  



class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(null=True , blank=True)
    phone_number = models.CharField(max_length=20 , null=True , blank=True)
    nin_number = models.PositiveIntegerField(null=True , blank=True)
    is_verified = models.BooleanField(default=False)
    school = models.ManyToManyField('schools.School', related_name='parent_schools')  


    @property
    def students(self):
        return Student.objects.filter(parent__user__identifier=self.user__identifier)



    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100 , null=True , blank=True)
    identifier = models.CharField(max_length=100, null=True , blank=True  , unique=True )
    parent = models.ForeignKey( 'accounts.ChannelUser', on_delete=models.SET_NULL , null=True , blank=True) 
    school = models.ForeignKey(School, on_delete=models.CASCADE , null=True , blank=True)
    channel = models.ForeignKey('schools.Channel', on_delete=models.CASCADE, null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 


 

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class AccountActivation(models.Model):
    email = models.EmailField()
    active_token = models.CharField(max_length=1000)



class ChannelUser(models.Model):
    identifier = models.CharField(max_length=17 , null=True , blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey('schools.Channel', on_delete=models.CASCADE)
    # the admin  is the user that created the channel 
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.user.email