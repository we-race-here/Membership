from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django import forms

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username',
               'required': True}))
    password = forms.CharField(widget=PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password',
               'required': True}))


class ProfileForm(forms.ModelForm):
    """
    User profile
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', ]
