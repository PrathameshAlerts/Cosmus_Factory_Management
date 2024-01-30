from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin , UserManager
from django.db import models


    
class CustomUserManager(BaseUserManager):
    def create_user(self, username,is_active= True,is_staff= False,is_admin= False, password=None, **extra_fields ): #takes in required fields username is required field as its a username field
        if not username:
            raise ValueError('users must have an email address')
        if not password:
            raise ValueError('users must have password')
        
        user_obj = self.model(username=username, **extra_fields) # The line is creating a new user instance (user) by calling the model constructor (self.model) and providing values for the username field and any additional fields specified in extra_fields
        user_obj.set_password(password) # The set_password method is typically called later to set the user's password before saving the user instance to the database.
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active   
        user_obj.save(using=self._db) # save user
        return user_obj

    def create_superuser(self, username, password=None, **extra_fields): #takes createuser and sets superuser attributes to true
        user = self.create_user(username, password = password, is_admin=True, is_staff=True)

        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    timestamp =  models.DateTimeField(auto_now=True)
    role_choices = [
        ('Super Admin', 'Super Admin'),
        ('Admin', 'Admin'),
        ('Store Manager', 'Store Manager'),
        ('Promoter', 'Promoter'),
        ('Wholesaler', 'Wholesaler'),
        ('Distributor', 'Distributor'),
        ('CG Partner', 'CG Partner'),
        ('Logistics', 'Logistics'),
        ('Account', 'Account'),
        ('Corporate Sales Person', 'Corporate Sales Person'),
        ('Trade Sales Person', 'Trade Sales Person'),
        ('Ecommerce Sales Person', 'Ecommerce Sales Person'),
        ('Modern Trade Sales Person', 'Modern Trade Sales Person'),
        ('Sales Coordinator', 'Sales Coordinator'),
        ('Production Manager', 'Production Manager'),
        ('Purchase Manager', 'Purchase Manager'),
        ('Customer', 'Customer'),
    ]
    role = models.CharField(max_length=30, choices=role_choices)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return
    
    def get_short_name(self):
        return
    
    @property
    def is_staff(self):
        return self.is_staff
    
    @property
    def is_admin(self):
        return self.is_admin
    
    @property
    def is_active(self):
        return self.active