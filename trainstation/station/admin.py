from django.contrib import admin

from station.models import Crew


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    filter_horizontal = ('journeys',)
