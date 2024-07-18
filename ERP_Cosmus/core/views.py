from django.shortcuts import redirect, render
from .forms import LoginForm
from .decorators import authenticated_user
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Company



@authenticated_user
def login_user(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request,data=request.POST)

        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username,password=password)

            if user is not None:
                login(request, user)
                messages.success(request,'Logged in successfully')
                return redirect('dashboard-main')
            else:
                messages.error(request,'Username or Password is incorrect')
                
    context = {'form':form}
    return render(request, 'core/login.html', context=context)


@login_required
def logout_user(request):
    logout(request)
    messages.success(request,'You have been logged out ')
    return redirect('login')


def create_update_delete_list_company(request,pk=None):

    company_all= Company.objects.all()