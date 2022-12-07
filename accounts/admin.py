from django.contrib import admin
from .models import AccountActivation, User  , Student , ChannelUser
from django.contrib.auth.admin import UserAdmin



class ChannelUserModelAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name',  'email' ,'is_parent','is_staff','is_admin' , 'created_at' , 'updated_at']  

class CustomUserAdminConfig(UserAdmin):     
    model = User
    search_fields = ('email', 'first_name',)   
    list_filter = ('email', 'first_name', 'is_active', 'is_staff')
    ordering = ('-created_at',)
    list_display = ('email', 'first_name','last_name', 'is_active', 'is_staff', 'is_superuser','is_verified') 
    fieldsets = (
        (None, {'fields': ('identifier','email', 'first_name',  'last_name', 'phone_number', 'address','gender' )}), 
        ('Permissions', {'fields': ('is_staff', 'is_active','is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email' , 'first_name',  'last_name',   'password1', 'password2', 'is_active', 'is_staff' )} 
         ),
    )





admin.site.register(User, CustomUserAdminConfig) 
admin.site.register(Student) 
admin.site.register(AccountActivation) 
admin.site.register(ChannelUser, ChannelUserModelAdmin) 
    