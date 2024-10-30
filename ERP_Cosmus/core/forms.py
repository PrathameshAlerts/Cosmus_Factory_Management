from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField ,PasswordChangeForm
from .models import CustomUser, Roles

from django.contrib.auth.forms import  AuthenticationForm

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget = forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget = forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role',)


    # validations for password 
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    # set password 
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    

class UserCreationFormAdmin(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget = forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget = forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'company')


    # validations for password 
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    # set password 
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name','password' ,'last_name', 'role', 'is_active', 'is_staff')

    def clean_password(self):
        return self.initial["password"]
    

class UserChangeFormAdmin(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name','password' ,'last_name', 'role', 'company', 'is_active', 'is_staff')

    def clean_password(self):
        return self.initial["password"]
    
class UserUpdateForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ["old_password", "new_password1", "new_password2"]


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())