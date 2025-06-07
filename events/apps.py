"""
Application configuration for the events package.
"""
from django.apps import AppConfig


class EventsConfig(AppConfig):
    """
    Configuration class for the events application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'
