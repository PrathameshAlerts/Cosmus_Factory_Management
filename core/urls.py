
from django.urls import path
from .views import list_company_users, create_company_user, edit_company_user, delete_company_user,login_user, logout_user, password_change_view, permission_denied_view

urlpatterns = [
    path('company/users/', list_company_users, name='list_company_users'),
    path('company/users/create/', create_company_user, name='create_company_user'),
    path('company/users/edit/<int:user_id>/', edit_company_user, name='edit_company_user'),
    path('company/users/delete/<int:user_id>/', delete_company_user, name='delete_company_user'),
    path('permission_denied', permission_denied_view, name='permission_denied'),
    path('login/',login_user, name='login'),
    path('logout/',logout_user, name='logout'),
    path('passwordchange/', password_change_view, name='password-change')
]