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
                
                # Check for the next parameter in the request
                next_url = request.GET.get('next')
                if not next_url:
                    # If no next parameter, check for the last visited URL in the session
                    next_url = request.session.get('last_visited_url')
                
                if next_url:
                    return redirect(next_url)
                
                # If no next parameter and no last visited URL, use the existing redirection logic
                if user.is_superuser:
                    return redirect('admin-dashboard')  # Redirect superuser to parish dashboard
                elif user.groups.filter(name='Clergyadmin').exists():
                    return redirect('dashboard')  # Redirect to clergy dashboard
                elif user.groups.filter(name='Parish Restructure Admin').exists():
                    return redirect('parish_dashboard')  # Redirect to parish dashboard
                elif user.groups.filter(name='TransferAdmin').exists():
                    return redirect('t_dashboard')  # Redirect to transfer admin dashboard
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            # If form validation fails, display error messages
            for field, errors in form.errors.items():
                if field == '__all__':
                    for error in errors:
                        messages.error(request, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')
                else:
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
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
