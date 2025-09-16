from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UserUpdateForm, ProfileUpdateForm, FirstTimePasswordChangeForm
from django.forms.utils import ErrorList
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash


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
                
                # Check if user needs to change password (first time login)
                if hasattr(user, 'userprofile') and not user.userprofile.password_changed:
                    messages.info(request, 'Please change your default password for security.')
                    return redirect('first_time_password_change')
                
                # Check for the next parameter in the request
                next_url = request.GET.get('next')
                # if not next_url:
                #     # If no next parameter, check for the last visited URL in the session
                #     next_url = request.session.get('last_visited_url')
                
                if next_url:
                    return redirect(next_url)
                
                # If no next parameter and no last visited URL, use the existing redirection logic
                if user.is_superuser:
                    return redirect('centralized_dashboard')  # Redirect superuser to main dashboard
                elif user.groups.filter(name='clergyadmin').exists():
                    return redirect('centralized_dashboard')  # Redirect to main dashboard
                elif user.groups.filter(name='parishadmin').exists():
                    return redirect('centralized_dashboard')  # Redirect to main dashboard
                elif user.groups.filter(name='transferadmin').exists():
                    return redirect('centralized_dashboard')  # Redirect to main dashboard
                else:
                    return redirect('centralized_dashboard')  # Default to main dashboard
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


@login_required
def first_time_password_change(request):
    """
    View for first-time password change by new users.
    Forces users to change their default password before accessing the system.
    """
    # Check if user has already changed their password
    if hasattr(request.user, 'userprofile') and request.user.userprofile.password_changed:
        messages.info(request, 'You have already changed your password.')
        return redirect('centralized_dashboard')

    if request.method == 'POST':
        form = FirstTimePasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # Save the new password
            form.save()
            # Update session auth hash to prevent logout
            update_session_auth_hash(request, form.user)
            # Mark password as changed
            if hasattr(request.user, 'userprofile'):
                request.user.userprofile.password_changed = True
                request.user.userprofile.save()
            # Show success message
            messages.success(request, 'Password changed successfully! Welcome to the system.')
            # Redirect to dashboard
            return redirect('centralized_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FirstTimePasswordChangeForm(request.user)

    context = {
        'form': form,
        'page_title': 'Change Your Password',
        'page_subtitle': 'For security reasons, please change your default password before continuing.',
        'is_first_time': True
    }

    return render(request, 'users/first_time_password_change.html', context)
