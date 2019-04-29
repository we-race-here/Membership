from django.conf import settings
from django.contrib.auth.views import PasswordChangeView
from django.core import signing
from django.core.mail import send_mail
from django.shortcuts import render, redirect

# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.generic import UpdateView, TemplateView

from apps.membership.forms import (ProfileBasicInfoForm, LoginForm, SignUpForm, ActivationSignUpForm,
                                   ForgotPasswordForm, PasswordRecoveryForm, ProfileRacerForm, ProfilePromotorStaffForm)
from apps.membership.models import User, Racer, StaffPromotor, Event
from race_membership.helpers.shortcuts import unsign
from race_membership.helpers.utils import PermissionRequiredMixin, success_message, send_form_errors, ex_reverse, \
    error_message


class IndexView(View):

    def get(self, request, *args, **kwargs):
        ctx = {}
        return render(request, 'membership/index.html', ctx)


class UiPanelView(View):
    def get(self, request, *args, **kwargs):
        return redirect('/static/vue/index.html')


class LoginView(View):
    template_name = 'membership/registration/signin.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        form = LoginForm()
        ctx = {'form': form}
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
        ctx = {'form': form}
        return render(request, self.template_name, ctx)


class SignUpView(View):
    template_name = 'membership/registration/signup.html'

    def _send_activation_email(self, email):
        sign = signing.dumps({'email': email}, salt=settings.SIGNUP_ACTIVATION_SALT)
        url = ex_reverse('membership:activation-signup', request=self.request, scheme='http', kwargs={'sign': sign})
        context = {
            'activation_url': url,
        }
        message = render_to_string('membership/email/signup-activation.html', context)
        subject = 'Race-Membership Registration'
        from_email = settings.DEFAULT_EMAIL_FROM
        return send_mail(subject, message, from_email, [email], html_message=message, fail_silently=False)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        form = SignUpForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            self._send_activation_email(form.cleaned_data['email'])
            success_message('Activation link sent to your email, please check your email.', request)
            return redirect(settings.LOGIN_URL)

        send_form_errors(form, request)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)


class ActivationSignUpView(View):
    template_name = 'membership/registration/activation-signup.html'
    sign_url_kwarg = 'sign'
    _unsigned_data = None

    def get_unsigned_args(self):
        if not self._unsigned_data:
            signed_data = self.kwargs.get(self.sign_url_kwarg)
            self._unsigned_data = unsign(signed_data, salt=settings.SIGNUP_ACTIVATION_SALT,
                                         max_age=settings.SIGNUP_ACTIVATION_AGE)
        return self._unsigned_data

    @property
    def email_address(self):
        return self.get_unsigned_args()['email'].lower()

    def get_context_data(self, **kwargs):
        kwargs['email'] = self.email_address
        return kwargs

    def exists_email(self):
        if User.objects.filter(email=self.email_address).exists():
            return True
        return False

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        if self.exists_email():
            error_message('An account with this email already registered!', request)
            return redirect(settings.LOGIN_REDIRECT_URL)
        form = ActivationSignUpForm()
        return render(request, self.template_name, self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        if self.exists_email():
            error_message('An account with this email already registered!', request)
            return redirect(settings.LOGIN_REDIRECT_URL)
        form = ActivationSignUpForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = self.email_address
            user.save()
            auth_login(request, user)
            success_message('Registration finished successfully.', request)
            return redirect('membership:index')

        return render(request, self.template_name, self.get_context_data(form=form))


class ForgotPasswordView(View):
    template_name = 'membership/registration/forgot-password.html'

    def _send_recovery_email(self, email):
        sign = signing.dumps({'email': email}, salt=settings.RECOVERY_PASSWORD_SALT)
        url = ex_reverse('membership:password-recovery', request=self.request, scheme='http', kwargs={'sign': sign})
        context = {
            'recovery_url': url,
        }
        message = render_to_string('membership/email/recovery-password.html', context)
        subject = 'Race-Membership Recovery Password'
        from_email = settings.DEFAULT_EMAIL_FROM
        return send_mail(subject, message, from_email, [email], html_message=message, fail_silently=False)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        form = ForgotPasswordForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(data=request.POST)
        if form.is_valid():
            self._send_recovery_email(form.cleaned_data['email'])
            success_message('Recovery password link sent to your email, please check your email.', request)
            return redirect(settings.LOGIN_URL)

        send_form_errors(form, request)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)


class PasswordRecoveryView(View):
    template_name = 'membership/registration/password-recovery.html'
    sign_url_kwarg = 'sign'
    _unsigned_data = None

    def get_unsigned_args(self):
        if not self._unsigned_data:
            signed_data = self.kwargs.get(self.sign_url_kwarg)
            self._unsigned_data = unsign(signed_data, salt=settings.RECOVERY_PASSWORD_SALT,
                                         max_age=settings.RECOVERY_PASSWORD_AGE)
        return self._unsigned_data

    @property
    def email_address(self):
        return self.get_unsigned_args()['email'].lower()

    def get_context_data(self, **kwargs):
        kwargs['email'] = self.email_address
        kwargs['current_user'] = self.get_user()
        return kwargs

    def get_user(self):
        return User.objects.filter(email=self.email_address).first()

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        user = self.get_user()
        if not user:
            error_message('No account registered with this email', request)
            return redirect(settings.LOGIN_REDIRECT_URL)
        form = PasswordRecoveryForm(user=user)
        return render(request, self.template_name, self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        user = self.get_user()
        if not user:
            error_message('No account registered with this email', request)
            return redirect(settings.LOGIN_REDIRECT_URL)
        form = PasswordRecoveryForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            success_message('Password reset successfully.', request)
            return redirect('membership:index')

        return render(request, self.template_name, self.get_context_data(form=form))


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        next_url = request.headers.get('Referer') or 'membership:index'
        return redirect(next_url)


class ProfileBasicInfoView(PermissionRequiredMixin, UpdateView):
    permission_required = ()
    form_class = ProfileBasicInfoForm
    template_name = 'membership/profile/basic_info.html'
    success_url = reverse_lazy('membership:profile-basic-info')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        result = super().form_valid(form)
        success_message('Basic Profile updated successfully.', self.request)
        return result


class ProfileRacerView(PermissionRequiredMixin, UpdateView):
    permission_required = ()
    form_class = ProfileRacerForm
    template_name = 'membership/profile/racer.html'
    success_url = reverse_lazy('membership:profile-racer')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        try:
            return self.request.user.racer
        except Racer.DoesNotExist:
            return None

    def form_valid(self, form):
        result = super().form_valid(form)
        success_message('Racer Profile updated successfully.', self.request)
        return result


class ProfilePromotorStaffView(PermissionRequiredMixin, UpdateView):
    permission_required = ()
    form_class = ProfilePromotorStaffForm
    template_name = 'membership/profile/promotor_staff.html'
    success_url = reverse_lazy('membership:profile-promotor-staff')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        try:
            return self.request.user.staff_promotor
        except StaffPromotor.DoesNotExist:
            return None

    def form_valid(self, form):
        result = super().form_valid(form)
        success_message('Staff Promotor Profile updated successfully.', self.request)
        return result


class ChangePasswordView(PermissionRequiredMixin, PasswordChangeView):
    permission_required = ()
    success_url = reverse_lazy('membership:change-password')
    template_name = 'membership/change_password.html'

    def form_valid(self, form):
        result = super(ChangePasswordView, self).form_valid(form)
        success_message('Password changed successfully.', self.request)
        return result


class EventListView(TemplateView):
    template_name = 'membership/event_list.html'


class EventCalendarView(TemplateView):
    template_name = 'membership/event_calendar.html'
