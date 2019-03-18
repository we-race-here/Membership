from django.conf import settings
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.generic import UpdateView

from apps.membership.forms import ProfileForm, LoginForm
from race_membership.helpers.utils import PermissionRequiredMixin, success_message, send_form_errors


class IndexView(PermissionRequiredMixin, View):
    permission_required = ()

    def get(self, request, *args, **kwargs):
        ctx = {}
        return render(request, "membership/index.html", ctx)


class LoginView(View):
    template_name = "membership/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        form = LoginForm()
        ctx = {"form": form}
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next = request.GET.get('next') or settings.LOGIN_REDIRECT_URL
            return redirect(next)
        else:
            send_form_errors(form, request)
        ctx = {"form": form}
        return render(request, self.template_name, ctx)


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return redirect(settings.LOGIN_URL)


class ProfileView(PermissionRequiredMixin, UpdateView):
    permission_required = ()
    form_class = ProfileForm
    template_name = 'membership/profile.html'
    success_url = reverse_lazy('membership:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        result = super(ProfileView, self).form_valid(form)
        success_message('Profile updated successfully.', self.request)
        return result


class ChangePasswordView(PermissionRequiredMixin, PasswordChangeView):
    permission_required = ()
    success_url = reverse_lazy('membership:change-password')
    template_name = 'membership/change_password.html'

    def form_valid(self, form):
        result = super(ChangePasswordView, self).form_valid(form)
        success_message('Password changed successfully.', self.request)
        return result
