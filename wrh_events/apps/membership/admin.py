from django import forms
from django.contrib import admin

from .models import User, StaffPromotor, Racer, Promotor, RaceCategory, RaceType, Race, RaceResult, Event, License, \
    RacerLicense


class RaceResultInline(admin.TabularInline):
    ordering = ("place",)
    model = RaceResult

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "racer":
            kwargs["queryset"] = Racer.objects.order_by('first_name', 'last_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BulkRaceForm(forms.ModelForm):
    pass


class BulkRaceAdmin(admin.ModelAdmin):
    inlines = [
        RaceResultInline,
    ]


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
