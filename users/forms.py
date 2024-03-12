from django import forms
from django.contrib.auth.models import User
from .models import *
class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        }
        
# class RegisterForm(LoginForm):
#     class Meta:
#         model = User
#         fields = ['username', 'password', 'email']
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
#             'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
#         }