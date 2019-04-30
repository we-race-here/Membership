from django.urls import include, path
from rest_framework import routers

from apps.membership.rest_api.views import (SessionView, ProfileView, EventView, RaceView, RaceResultView)

rest_router = routers.DefaultRouter()
rest_router.trailing_slash = "/?"  # added to support both / and slashless
rest_router.register(r'session', SessionView, basename='session')
rest_router.register(r'me', ProfileView, basename='profile')
rest_router.register(r'event', EventView)
rest_router.register(r'race', RaceView)
rest_router.register(r'race_result', RaceResultView)

app_name = 'membership'
urlpatterns = [
    path('', include(rest_router.urls))
]
