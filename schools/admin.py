from django.contrib import admin
from .models import Channel , StudentPickUpVerification
# Register your models here.



class CustomStudentPickUpVerificationModelAdmin(admin.ModelAdmin):
    list_display = ['student','completed',  'date' , 'created_at' , 'updated_at'] 

admin.site.register(StudentPickUpVerification , CustomStudentPickUpVerificationModelAdmin)   
admin.site.register(Channel)   