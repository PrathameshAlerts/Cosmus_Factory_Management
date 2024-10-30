from django.http import HttpResponse
from django.shortcuts import redirect

# does not allow logged in users to login route
def authenticated_user(view_func):

    def wrapper_function(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard-main')
        else:
            return view_func(request, *args, **kwargs) 
    
    return wrapper_function

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request,*args, **kwargs):
            return view_func(request,*args, **kwargs)
        return wrapper_func
    return decorator