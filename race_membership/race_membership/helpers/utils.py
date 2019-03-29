import functools
import random
import string
import traceback

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render
from sendsms import api
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.core.mail.backends.filebased import EmailBackend
from django.contrib.auth.mixins import PermissionRequiredMixin as \
    DjangoPermissionRequiredMixin

print = functools.partial(print, flush=True)


class PermissionRequiredMixin(DjangoPermissionRequiredMixin):

    def get_permission_required(self):
        perms = self.permission_required or ()
        if isinstance(perms, dict):
            perms = perms.get(self.request.method.lower(), ()) or ()

        if isinstance(perms, str):
            perms = (perms,)

        return perms

    def handle_no_authenticated(self):
        if self.request.is_ajax():
            return JsonResponse({'error': 'Not Authorized'}, status=401)
        return redirect_to_login(self.request.get_full_path(),
                                 self.get_login_url(),
                                 self.get_redirect_field_name())

    def handle_no_permission(self):
        if self.request.is_ajax():
            return JsonResponse({'error': 'Permission Denied'}, status=403)
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return render(self.request, "no-permission.html", status=403)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_authenticated()
        if not self.has_permission():
            return self.handle_no_permission()
        return super(PermissionRequiredMixin, self
                     ).dispatch(request, *args, **kwargs)

class CustomFileBasedEmailBackend(EmailBackend):
    def write_message(self, message):
        res = super(CustomFileBasedEmailBackend, self).write_message(message)
        if getattr(settings, 'EMAIL_BODY_TO_FILE'):
            try:
                with open(settings.EMAIL_BODY_TO_FILE, 'w') as f:
                    f.write(str(message.body))
            except Exception:
                traceback.print_exc()
        if getattr(settings, 'EMAIL_BODY_TO_CONSOLE') is True:
            print(message.body)
        return res


def random_id(n=8, no_upper=False, no_lower=False, no_digit=False):
    rand = random.SystemRandom()
    chars = ''
    if no_upper is False:
        chars += string.ascii_uppercase
    if no_lower is False:
        chars += string.ascii_lowercase
    if no_digit is False:
        chars += string.digits
    if not chars:
        raise Exception('chars is empty! change function args!')
    return ''.join([rand.choice(chars) for _ in range(n)])


def send_sms(message, to, from_=None, fail_silently=False):
    from_ = from_ or settings.SMS_DEFAULT_FROM_PHONE
    if isinstance(to, str):
        to = [to]
    return api.send_sms(body=message, from_phone=from_, to=to, fail_silently=fail_silently)


def ex_reverse(viewname, **kwargs):
    if viewname.startswith('http://') or viewname.startswith('https://'):
        return viewname

    host = kwargs.pop('hostname', None)
    request = kwargs.pop('request', None)
    scheme = kwargs.pop('scheme', None)
    if not host:
        host = request.get_host() if request else settings.HOSTNAME

    if not viewname:
        rel_path = ''
    elif viewname.startswith('/'):
        rel_path = viewname
    else:
        rel_path = reverse(viewname, **kwargs)

    scheme = '{}://'.format(scheme) if scheme else ''

    return '{0}{1}{2}'.format(scheme, host, rel_path)


class NotSet(object):
    pass


def capitalize_first(s):
    if s:
        return s[0].upper() + s[1:]
    return s


def netref_to_native(d):
    if isinstance(d, dict):
        return {k: netref_to_native(v) for k, v in d.items()}
    if isinstance(d, list):
        return list(netref_to_native(v) for v in d)
    if isinstance(d, tuple):
        return tuple(netref_to_native(v) for v in d)
    if isinstance(d, set):
        return set(netref_to_native(v) for v in d)
    return d


def success_message(message, request):
    return messages.success(request, mark_safe(message))


def error_message(message, request):
    return messages.error(request, mark_safe(message), extra_tags='danger')


def info_message(message, request):
    return messages.info(request, mark_safe(message))


def warning_message(message, request):
    return messages.warning(request, mark_safe(message))


def send_form_errors(form, request):
    msgs = []
    for k, v in form.errors.items():
        msg = '' if k.startswith('__') else '{0}: '.format(k)
        msgs.append('<li>{0}{1}</li>'.format(msg, ', '.join(v)))

    if msgs:
        return error_message(''.join(msgs), request)
