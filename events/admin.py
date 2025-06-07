"""
Admin configuration for event and registration models.
"""
from django.contrib import admin
from events.models import Event, Registration


class EventAdmin(admin.ModelAdmin):
    """
    Admin interface for the Event model. Displays title and date.
    """
    model = Event
    list_display = ('title', 'date')
    search_fields = ('title', 'date')


class RegistrationAdmin(admin.ModelAdmin):
    """
    Admin interface for the Registration model. Displays event
    title and registered email.
    """
    model = Registration
    list_display = ('event', 'email')
    search_fields = ('event', 'email')
    list_filter = ('event',)


admin.site.register(Event, EventAdmin)
admin.site.register(Registration, RegistrationAdmin)
