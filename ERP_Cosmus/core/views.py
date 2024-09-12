from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .forms import LoginForm, UserCreationForm, UserChangeForm
from .decorators import authenticated_user
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

@login_required
def list_company_users(request):
    if not request.user.is_staff:
        return redirect('permission_denied')

    company_users = CustomUser.objects.filter(company=request.user.company)
    return render(request, 'core/company_users_list.html', {'users': company_users})


@login_required
def create_company_user(request):
    if not request.user.is_staff:
        return redirect('permission_denied')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.company = request.user.company  # set the user to the current admin's company
            user.save()
            return redirect('list_company_users')
    else:
        form = UserCreationForm()

    return render(request, 'core/create_company_user.html', {'form': form ,'user_name':request.user.username,'company_name':request.user.company.name})


@login_required
def edit_company_user(request, user_id):
    if not request.user.is_staff:
        return redirect('permission_denied')

    user = get_object_or_404(CustomUser, id=user_id, company=request.user.company)

    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('list_company_users')
    else:
        form = UserChangeForm(instance=user)

    return render(request, 'core/edit_company_user.html', {'form': form, 'user': user})

@login_required
def delete_company_user(request, user_id):
    if not request.user.is_staff:
        return redirect('permission_denied')

    user = get_object_or_404(CustomUser, id=user_id, company=request.user.company)
    
    if request.method == 'POST':
        user.delete()
        return redirect('list_company_users')

    return render(request, 'core/delete_company_user.html', {'user': user})


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


def permission_denied_view(request):
    return render(request,'core/permission_denied_html.html')