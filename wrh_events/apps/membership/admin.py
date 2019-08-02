from django import forms
from django.contrib import admin

from .models import User, StaffPromotor, Racer, Promotor, RaceCategory, RaceType, Race, RaceResult, Event, License, RacerLicense


class RaceResultInline(admin.TabularInline):
    model = RaceResult


class BulkRaceForm(forms.ModelForm):
    pass


class BulkRaceAdmin(admin.ModelAdmin):
    inlines = [
        RaceResultInline,
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


admin.site.register(User)
admin.site.register(StaffPromotor)
admin.site.register(Racer)
admin.site.register(Promotor)
admin.site.register(RaceCategory)
admin.site.register(RaceType)
admin.site.register(Race, BulkRaceAdmin)
admin.site.register(RaceResult)
admin.site.register(Event)
admin.site.register(License)
admin.site.register(RacerLicense)

