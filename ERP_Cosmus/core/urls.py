
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [

    #authentication routes
    path('',views.login , name='login'), 
    path('logout/',views.logout , name='logout'),
] 
