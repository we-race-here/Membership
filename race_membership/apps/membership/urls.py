from django.urls import re_path
from .views import (
    IndexView, LoginView, LogoutView, ProfileBasicInfoView, ChangePasswordView, SignUpView,
    ActivationSignUpView, ForgotPasswordView, PasswordRecoveryView, ProfileRacerView, ProfilePromotorStaffView,
    UiPanelView, EventListView, EventCalendarView)

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
    re_path(r'^change-password/$', ChangePasswordView.as_view(), name="change-password"),
    re_path(r'^profile-basic-info/$', ProfileBasicInfoView.as_view(), name="profile-basic-info"),
    re_path(r'^profile-racer/$', ProfileRacerView.as_view(), name="profile-racer"),
    re_path(r'^profile-promotor-staff/$', ProfilePromotorStaffView.as_view(), name="profile-promotor-staff"),
    re_path(r'^event-list/$', EventListView.as_view(), name="event-list"),
    re_path(r'^event-calendar/$', EventCalendarView.as_view(), name="event-calendar"),

]
