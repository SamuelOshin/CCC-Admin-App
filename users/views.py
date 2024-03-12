from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group


#Login a user
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                messages.success(request, 'Login Successful.')
                if user.groups.filter(name='Clergyadmin').exists():
                    return redirect('dashboard')  # Redirect to clergy dashboard
                else:
                    return redirect('parish_dashboard')  # Redirect to parish dashboard
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            # If form validation fails, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})
#logout a user



def logout_user(request):
    logout(request)
    messages.info(request, 'Logout Successfully, your session has ended.')
    return redirect('login_user')