from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.core import exceptions as django_exceptions

from apps.membership.models import User, Racer, StaffPromotor, Event, Promotor, RaceResult
from race_membership.helpers.utils import DynamicFieldsSerializerMixin, Base64ImageField


class SessionSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=128, style={'input_type': 'password'})
    remember = serializers.BooleanField(initial=False, required=False)


class PermissionSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename')


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})
    current_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'invalid_password': 'Invalid Password',
    }

    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail('invalid_password')

    def validate_new_password(self, new_password):
        try:
            validate_password(new_password, self.context['request'].user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return new_password


class NestedGroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(read_only=True, many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions')


class RacerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racer
        fields = '__all__'
        read_only_fields = ('uid', 'user', 'first_name', 'last_name', 'licenses')


class StaffPromotorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffPromotor
        fields = '__all__'
        read_only_fields = ('user', 'promotors', 'first_name', 'last_name')


class UserSessionSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    user_permissions = PermissionSerializer(read_only=True, many=True)
    groups = NestedGroupSerializer(read_only=True, many=True)

    class Meta:
        model = User
        exclude = ('password',)


class UserProfileSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, trim_whitespace=True)
    last_name = serializers.CharField(required=True, trim_whitespace=True)
    avatar = Base64ImageField(required=False, allow_null=True)
    racer = RacerProfileSerializer(required=False, allow_null=True)
    staff_promotor = StaffPromotorProfileSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'avatar', 'is_staff_promotor', 'is_racer',
                  'racer', 'staff_promotor')
        read_only_fields = ('email', 'username')

    @transaction.atomic()
    def update(self, instance, validated_data):
        racer_data = validated_data.pop('racer', {})
        try:
            racer_object = instance.racer
        except Racer.DoesNotExist:
            racer_object = None
        if racer_data:
            if not racer_object:
                racer_object = Racer(user=instance)
            for k, v in racer_data.items():
                setattr(racer_object, k, v)
            racer_object.save()
        elif (not racer_object) and validated_data.get('is_racer'):
            raise serializers.ValidationError('Cannot enable racer profile before complete required fields!')

        staff_promotor_data = validated_data.pop('staff_promotor', {})
        if staff_promotor_data:
            try:
                staff_promotor_object = instance.staff_promotor
            except StaffPromotor.DoesNotExist:
                staff_promotor_object = None
            if not staff_promotor_object:
                staff_promotor_object = StaffPromotor(user=instance)
            for k, v in staff_promotor_data.items():
                setattr(staff_promotor_object, k, v)
            staff_promotor_object.save()

        return super(UserProfileSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        res = super(UserProfileSerializer, self).to_representation(instance)
        if not res.get('racer'):
            res['racer'] = {}
        if not res.get('staff_promotor'):
            res['staff_promotor'] = {}
        return res


class NestedPromotorSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Promotor
        fields = ('id', 'name',)


class EventSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    _promotor = NestedPromotorSerializer(read_only=True, source='promotor')

    class Meta:
        model = Event
        fields = '__all__'


class RaceResultSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    @staticmethod
    def get_full_name(race_result):
        return '{} {}'.format(race_result.racer.first_name, race_result.racer.last_name)

    class Meta:
        model = RaceResult
        fields = ('place', 'duration', 'full_name')
