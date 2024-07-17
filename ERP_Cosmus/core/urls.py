
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [

    #authentication routes
    path('login/',views.login_user , name='login'), 
    path('logout/',views.logout_user , name='logout'),
] 
