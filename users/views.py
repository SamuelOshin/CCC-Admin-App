from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UserUpdateForm, ProfileUpdateForm
from django.forms.utils import ErrorList
from django.contrib.auth.decorators import login_required


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


# def edit_profile(request):
#     user = request.user  # Retrieve the current user
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, instance=user)
#         if form.is_valid():
#             form.save()  # Save the form to update the user's profile
#             messages.success(request, 'Profile updated successfully.')
#             return redirect('edit_profile')
#         else:
#                 # Retrieve form errors and append them to messages.error
#             error_messages = ErrorList(form.errors.values())
#             for message in error_messages:
#                 messages.error(request, message)
#     else:
#         form = ProfileForm(instance=user)  # Populate form with user data
#     return render(request, 'profile.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.userprofile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('edit_profile') # Redirect back to profile page
        else:
            messages.error(request, f'Error updating your profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profile.html', context)
