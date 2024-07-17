from django.shortcuts import redirect, render
from .forms import LoginForm
from django.contrib.auth.models import auth
from .decorators import authenticated_user
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@authenticated_user
def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request,data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(request, username=username,password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('dashboard-main')
    context = {'form':form}
    return render(request, 'core/login.html', context=context)


@login_required
def logout(request):
    auth.logout(request)
    messages.success(request,'You have been logged out ')
    return redirect('login')