from django.urls import re_path
from .views import (
    IndexView, LoginView, LogoutView, SignUpView, ActivationSignUpView, ForgotPasswordView, PasswordRecoveryView,
    UiPanelView, EventListView, EventCalendarView, RaceResultView
)

app_name = 'membership'

urlpatterns = [
    re_path(r'^$', IndexView.as_view(), name='index'),
    re_path(r'^ui-panel/$', UiPanelView.as_view(), name='ui-panel'),
    re_path(r'^login/$', LoginView.as_view(), name="login"),
    re_path(r'^logout/$', LogoutView.as_view(), name="logout"),
    re_path(r'^signup/$', SignUpView.as_view(), name="signup"),
    re_path(r'^activation-signup/(?P<sign>.+)/$', ActivationSignUpView.as_view(), name="activation-signup"),
    re_path(r'^forgot-password/$', ForgotPasswordView.as_view(), name="forgot-password"),
    re_path(r'^password-recovery/(?P<sign>.+)/$', PasswordRecoveryView.as_view(), name="password-recovery"),
    re_path(r'^event-list/$', EventListView.as_view(), name="event-list"),
    re_path(r'^event-calendar/$', EventCalendarView.as_view(), name="event-calendar"),
    re_path(r'^race-result/(?P<event_id>\d+)/$', RaceResultView.as_view(), name="race-result"),
]
