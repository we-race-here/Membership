from datetime import timedelta

import django_filters
import simplejson as json
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django_filters import rest_framework as filters
from djoser.views import SetPasswordView as JoserSetPasswordView
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from reversion.models import Version

from apps.membership.rest_api.serializers import SessionSerializer, UserSessionSerializer, UserProfileSerializer
from race_membership.helpers.utils import ExtendedOrderingFilterBackend


class HistoricalViewMixin(object):
    """ NOTICE!!! This class should be as a first argument in multi-inheritance"""

    # set fields_for_check_changes = None in view to ignore changes checking
    fields_for_check_changes = '__all__'
    exclude_fields_for_check_changes = None
    search_fields = None
    extra_ordering_fields = {}
    class HistoryFilter(filters.FilterSet):
        min_date = django_filters.IsoDateTimeFilter(field_name="revision__date_created", lookup_expr="gte")
        max_date = django_filters.IsoDateTimeFilter(field_name="revision__date_created", lookup_expr="lte")

        class Meta:
            model = Version
            fields = ['id', 'min_date', 'max_date']

    @action(detail=False, filter_class=HistoryFilter, url_path='(?P<pk>[0-9]+)/history',
            ordering_fields=['id'], extra_ordering_fields={'date': 'revision__date_created'}, search_fields=[],
            filter_backends=(SearchFilter, ExtendedOrderingFilterBackend),
            ordering='id')
    def history(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        self.check_object_permissions(request, instance)
        qs = self.filter_class(data=request.GET, queryset=Version.objects.get_for_object(instance)).qs
        filtered_qs = self.filter_queryset(qs)
        page = self.paginate_queryset(filtered_qs)
        no_page = False
        if page is None:
            page = filtered_qs
            no_page =True
        result = []
        for h in page:
            json_data = h.serialized_data
            obj = json.loads(json_data)[0]["fields"]
            revision = h.revision
            user = revision.user
            if user:
                user = {
                    'id': user.id,
                    'username': user.username,
                }
            result.append({
                'object': obj,
                'id': h.pk,
                'user': user,
                'date': revision.date_created
            })

        return Response(result) if no_page else self.get_paginated_response(result)

    def _get_modified_fields(self, serializer):
        fields = self.fields_for_check_changes
        instance = serializer.instance
        if (self.exclude_fields_for_check_changes is not None) and fields is None:
            fields = '__all__'
        if fields == '__all__':
            fields = [f.name for f in instance.__class__._meta.fields]

        exclude_fields = self.exclude_fields_for_check_changes or []
        data = serializer.validated_data
        modified = {}
        for f in fields:
            field = serializer.fields[f]
            if f in exclude_fields or field.read_only:
                continue
            value = data.get(f)
            if getattr(instance, f, None) != value:
                modified[f] = value
        return modified

    # TODO: _get_modified_fields doesn't check many-to-many relationships
    # def perform_update(self, serializer):
    #     if self.fields_for_check_changes or self.exclude_fields_for_check_changes:
    #         modified = self._get_modified_fields(serializer)
    #         if not modified:
    #             return
    #     return serializer.save()


class SessionView(viewsets.ViewSet):
    class SessionPermission(permissions.BasePermission):
        """ custom class to check permissions for sessions """

        def has_permission(self, request, view):
            """ check request permissions """
            if request.method == 'POST':
                return True
            return request.user.is_authenticated and request.user.is_active

    permission_classes = (SessionPermission,)
    serializer_class = SessionSerializer

    def get(self, request, *args, **kwargs):
        """ api to get current session """
        return Response(UserSessionSerializer(request.user, context={'request': request}).data)

    def post(self, request, *args, **kwargs):
        """ api to login """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.data)
        if not user:
            return Response({'reason': 'Username or password is incorrect'}, status=400)
        if not user.is_active:
            return Response({'reason': 'User is inactive'}, status=403)

        login(request, user)
        return Response(UserSessionSerializer(user, context={'request': request}).data)

    def delete(self, request, *args, **kwargs):
        """ api to logout """

        user_id = request.user.id
        logout(request)
        return Response({'id': user_id})

    create = post  # this is a trick to show this view in api-root


class ProfileView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer
    parser_classes = list(viewsets.ViewSet.parser_classes) + [FileUploadParser]

    def list(self, request, *args, **kwargs):
        return Response(self.serializer_class(request.user, context={'request': request}).data)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(self.serializer_class(user, context={'request': request}).data)

    create = put


class SetPasswordView(JoserSetPasswordView):
    pass