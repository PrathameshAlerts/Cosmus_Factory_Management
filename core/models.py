from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin , UserManager , Group
from django.db import models
from django.core.validators import  MinLengthValidator, MaxLengthValidator
from django.db.models.signals import m2m_changed
from django.dispatch import receiver


class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length = 15, validators = [MinLengthValidator(15), MaxLengthValidator(15)])

    def __str__(self):
        return self.name
    

class Roles(models.Model):
    user_type = models.CharField(max_length = 100, default='base_user') 

    def __str__(self):
        return self.user_type

    
class CustomUserManager(BaseUserManager):

    def create_user(self, username,is_active= True, is_superuser=False, is_staff= False, password=None, **extra_fields ): 
        if not username:
            raise ValueError('users must have an User Name')
        
        if not password:
            raise ValueError('users must have password')
        
        user_obj = self.model(username=username, **extra_fields) 
        user_obj.set_password(password) 
        user_obj.is_staff = is_staff
        user_obj.is_active = is_active
        user_obj.is_superuser = is_superuser
        user_obj.save(using=self._db) 

        
        self.update_user_groups(user_obj)

        return user_obj

    def create_superuser(self, username, password=None, **extra_fields): 
        user = self.create_user(username, password = password, is_superuser=True , is_staff=True)

        return user
    
    def update_user_groups(self, user):
        
        user.groups.clear()
        
        for role in user.role.all():
            group, created = Group.objects.get_or_create(name = role.user_type)
            user.groups.add(group)
        user.save()


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField()
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    timestamp =  models.DateTimeField(auto_now=True)
    role = models.ManyToManyField(Roles)
    company = models.ForeignKey(Company, on_delete = models.CASCADE, null=True, blank=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    






@receiver(m2m_changed, sender=CustomUser.role.through)
def update_user_groups_on_role_change(sender, instance, action, **kwargs):
    """
    Signal handler to update groups based on role changes.
    Triggered when roles are added, removed, or cleared.
    """
    if action in ["post_add", "post_remove", "post_clear"]:
        CustomUser.objects.update_user_groups(instance)  



        """
        
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
        """