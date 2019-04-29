import os
import random
import string
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


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


def get_random_upload_path(upload_dir, filename, include_date=False):
    ext = filename.split('.')[-1]
    randid = random_id(n=8)
    filename = "{0}-{1}.{2}".format(uuid.uuid4(), randid, ext)
    if include_date:
        filename = '{}-{}'.format(timezone.now().strftime('%Y%m%d%H%M%S'), filename)
    return os.path.join(upload_dir, filename)


def avatar_file_path_func(instance, filename):
    return get_random_upload_path(os.path.join('uploads', 'user', 'avatar'), filename)


def event_flyer_path_func(instance, filename):
    return get_random_upload_path(os.path.join('uploads', 'event', 'flyer'), filename)


def event_image_file_path_func(instance, filename):
    return get_random_upload_path(os.path.join('uploads', 'event', 'image'), filename)


class User(AbstractUser):
    GENDER_MALE = 'm'
    GENDER_FEMALE = 'f'
    GENDER_OTHER = 'o'
    GENDER_UNKNOWN = 'u'
    GENDER_CHOICES = (
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
        (GENDER_UNKNOWN, 'Unknown'),
    )
    email = models.EmailField(null=True, unique=True)
    is_racer = models.BooleanField(default=False)
    is_staff_promotor = models.BooleanField(default=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_UNKNOWN)
    avatar = models.ImageField(blank=True, null=True, upload_to=avatar_file_path_func)

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()
        super().save(*args, **kwargs)


class Racer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='racer')
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    uid = models.CharField('Racer ID', max_length=16, unique=True, editable=False)
    birth_date = models.DateField()
    phone = PhoneNumberField(max_length=50, null=True, blank=True)
    street_address = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    race_category = models.ForeignKey('RaceCategory', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='racer')
    licenses = models.ManyToManyField('License', through='RacerLicense', blank=True)

    @property
    def year_age(self):
        today = timezone.now().date()
        return today.year - self.birth_date.year

    def make_uid_auto(self):
        bd = self.birth_date
        if not bd:
            raise AssertionError('birth_date is required')
        sid = '{:02d}{:02d}{:02d}'.format(bd.year % 100, bd.month, bd.day)
        idx = 1
        while True:
            uid = '{}{:03d}'.format(sid, idx)
            exists_qs = Racer.objects.filter(uid=uid)
            if self.pk:
                exists_qs = exists_qs.exclude(id=self.pk)
            if exists_qs.exists():
                idx += 1
            else:
                break
        return uid

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = self.make_uid_auto()
        if not self.first_name:
            self.first_name = self.user and self.user.first_name
        if not self.last_name:
            self.last_name = self.user and self.user.last_name
        return super().save(*args, **kwargs)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class StaffPromotor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_promotor')
    promotors = models.ManyToManyField('Promotor')

    def __str__(self):
        return str(self.user)


class Promotor(models.Model):
    name = models.CharField(max_length=256, unique=True)
    public_email = models.EmailField(unique=True)
    private_email = models.EmailField(unique=True)
    phone = PhoneNumberField(max_length=50, null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    facebook_url = models.URLField(null=True, blank=True)
    street_address = models.CharField(max_length=256, blank=True, null=True)
    street_address2 = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name


class RaceCategory(models.Model):
    name = models.CharField(max_length=256, unique=True)
    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)
    level = models.CharField(max_length=16)
    level_name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class RaceType(models.Model):
    title = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.title


class Race(models.Model):
    name = models.CharField(max_length=128)
    start_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    types = models.ManyToManyField(RaceType, blank=True)
    category = models.ForeignKey('RaceCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='race')
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='race')

    def __str__(self):
        return str(self.name)


class RaceResult(models.Model):
    # race duration, example, 1hr43min. Place, example 2nd, 6th place
    racer = models.ForeignKey(Racer, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    duration = models.DurationField()
    place = models.PositiveIntegerField()

    def __str__(self):
        return '{}- {}'.format(self.place, self.racer)


class Event(models.Model):
    name = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=128)
    map_latitude = models.DecimalField(max_digits=9, decimal_places=7, null=True, blank=True)
    map_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    promotor = models.ForeignKey(Promotor, on_delete=models.CASCADE)
    event_url = models.URLField(null=True, blank=True)
    event_flyer = models.FileField(max_length=256, null=True, blank=True, upload_to=event_flyer_path_func)
    image = models.ImageField(blank=True, null=True, upload_to=event_image_file_path_func)

    def __str__(self):
        return str(self.name)


class License(models.Model):
    name = models.CharField(max_length=128, unique=True)
    organization = models.CharField(max_length=256)

    class Meta:
        unique_together = (('name', 'organization',),)

    def __str__(self):
        return self.name


class RacerLicense(models.Model):
    license = models.ForeignKey(License, on_delete=models.CASCADE)
    racer = models.ForeignKey('Racer', on_delete=models.CASCADE)
    number = models.CharField(max_length=32)

    class Meta:
        unique_together = (('license', 'number',),)

    def __str__(self):
        return str(self.license)


# class Tag(models.Model):
#     pass
