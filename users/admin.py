from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
from .models import UserProfile
from django.contrib.auth.hashers import make_password


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form that generates a default password
    and marks the user as requiring password change.
    """
    generate_default_password = forms.BooleanField(
        required=False,
        initial=True,
        label="Generate default password",
        help_text="If checked, a secure default password will be generated and the user will be required to change it on first login."
    )

    default_password = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Leave empty to generate random password'}),
        label="Custom Default Password",
        help_text="Optional: Set a custom default password. If left empty and 'Generate default password' is checked, a random password will be created."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'groups', 'is_staff', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password fields not required initially - we'll handle validation in clean()
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['placeholder'] = 'Leave empty when generating default password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Leave empty when generating default password'

    def clean_password1(self):
        """Allow password1 to be empty when generating default password."""
        return self.cleaned_data.get('password1')

    def clean_password2(self):
        """Allow password2 to be empty when generating default password."""
        return self.cleaned_data.get('password2')

    def clean(self):
        """Override form validation to handle custom password logic."""
        cleaned_data = super().clean()
        generate_default = cleaned_data.get('generate_default_password')
        default_password = cleaned_data.get('default_password')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if generate_default:
            # When generating default password, validate custom password if provided
            if default_password and len(default_password) < 8:
                raise forms.ValidationError("Custom password must be at least 8 characters long.")
            # Password fields can be empty when generating default password
        else:
            # When not generating default password, require password1 and password2
            if not password1:
                raise forms.ValidationError("Password is required when not generating default password.")
            if not password2:
                raise forms.ValidationError("Password confirmation is required when not generating default password.")
            if password1 != password2:
                raise forms.ValidationError("Passwords don't match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        # Handle password generation
        if self.cleaned_data.get('generate_default_password'):
            if self.cleaned_data.get('default_password'):
                # Use custom password
                password = self.cleaned_data['default_password']
            else:
                # Generate random password
                password = get_random_string(length=12, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*')

            user.password = make_password(password)

            # Store the generated/used password in the form for display
            self.generated_password = password

            if commit:
                user.save()
                # Create or update user profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.password_changed = False  # Force password change
                profile.save()
        else:
            # Use the provided password from password1 field
            if commit:
                user.save()
                # Create or update user profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.password_changed = True  # Password is already set by user
                profile.save()

        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Custom user change form that shows password change status.
    """
    password_changed = forms.BooleanField(
        required=False,
        label="Password Changed",
        help_text="Indicates if the user has changed their initial password."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'groups', 'is_staff', 'is_active', 'password_changed')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'userprofile'):
            self.fields['password_changed'].initial = self.instance.userprofile.password_changed


class CustomUserAdmin(UserAdmin):
    """
    Custom User admin that supports default password generation
    and password change requirement tracking.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'password_changed_status', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Password Management', {
            'fields': ('password_changed',),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'groups', 'is_staff', 'is_active', 'generate_default_password', 'default_password'),
        }),
    )

    def password_changed_status(self, obj):
        """Display password change status in admin list."""
        if hasattr(obj, 'userprofile'):
            if obj.userprofile.password_changed:
                return '✓ Changed'
            else:
                return '⚠ Requires Change'
        return 'Unknown'
    password_changed_status.short_description = 'Password Status'

    def save_model(self, request, obj, form, change):
        """Override save_model to handle password change status updates."""
        super().save_model(request, obj, form, change)

        if not change:  # Only for new users
            # Check if a password was generated
            if hasattr(form, 'generated_password'):
                password = form.generated_password
                messages.success(
                    request,
                    mark_safe(
                        f'User "{obj.username}" was created successfully. '
                        f'Default password: <strong>{password}</strong><br>'
                        f'<small class="text-muted">Please save this password securely and provide it to the user.</small>'
                    )
                )

        if change and 'password_changed' in form.cleaned_data:
            profile, created = UserProfile.objects.get_or_create(user=obj)
            profile.password_changed = form.cleaned_data['password_changed']
            profile.save()

    def save_formset(self, request, form, formset, change):
        """Override save_formset to handle inline formsets if needed."""
        super().save_formset(request, form, formset, change)


# Register the custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register UserProfile
admin.site.register(UserProfile)