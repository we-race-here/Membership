from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from .models import User, StaffPromotor, Racer, Promotor, RaceCategory, RaceType, Race, RaceResult, Event, License, RacerLicense


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('is_racer', 'is_staff_promotor', 'gender', 'avatar')}),
    )


admin.site.register(User, MyUserAdmin)
admin.site.register(StaffPromotor)
admin.site.register(Racer)
admin.site.register(Promotor)
admin.site.register(RaceCategory)
admin.site.register(RaceType)
admin.site.register(Race)
admin.site.register(RaceResult)
admin.site.register(Event)
admin.site.register(License)
admin.site.register(RacerLicense)

