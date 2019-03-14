from django.urls import re_path
from .views import IndexView, LoginView, LogoutView, ProfileView, ChangePasswordView

app_name = 'membership'

urlpatterns = [
    re_path(r'^$', IndexView.as_view(), name='index'),
    re_path(r'^login/$', LoginView.as_view(), name="login"),
    re_path(r'^logout/$', LogoutView.as_view(), name="logout"),
    re_path(r'^profile/$', ProfileView.as_view(), name="profile"),
    re_path(r'^change-password/$', ChangePasswordView.as_view(), name="change-password"),
]
