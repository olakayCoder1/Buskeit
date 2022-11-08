from django.contrib import admin
from .models import AccountActivation, User  , Student , Parent , ChannelUser
from django.contrib.auth.admin import UserAdmin


class CustomUserAdminConfig(UserAdmin):
    model = User
    search_fields = ('email', 'first_name',)
    list_filter = ('email', 'first_name', 'is_active', 'is_staff')
    ordering = ('-created_at',)
    list_display = ('email', 'first_name','last_name', 'is_active', 'is_staff', 'is_superuser') 
    fieldsets = (
        (None, {'fields': ('email', 'first_name',  'last_name', 'phone_number', 'nin_number', 'address' )}), 
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email' , 'first_name',  'last_name',   'password1', 'password2', 'is_active', 'is_staff' )} 
         ),
    )





admin.site.register(User, CustomUserAdminConfig) 
admin.site.register(Student) 
admin.site.register(Parent) 
admin.site.register(AccountActivation) 
admin.site.register(ChannelUser) 
    