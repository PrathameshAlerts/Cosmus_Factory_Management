from django.contrib import admin

from .models import CustomUser

from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin


admin.site.site_header = 'Cosmus Management Pannel'

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = CustomUser

    # for list page
    list_display = ('username', 'is_staff', 'is_active')
    list_filter = ('username','is_staff', 'is_active',)


    # for detail page
    fieldsets = (
        (None, {'fields': ('username', 'password',)}),
        ('Permissions', {'fields': ('is_staff' , 'is_active', )}),

        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('groups', 'user_permissions',),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),   # class for css 
            'fields': ('email','username' ,'password1', 'password2', 'is_staff', 'is_active',)} # fields shown on create user page on admin panel
        ),
    )
    
admin.site.register(CustomUser, CustomUserAdmin)