from django import forms
from django.contrib.auth.forms import  UserChangeForm , UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth.models import Group






class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email',)




class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())