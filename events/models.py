"""Models for events package."""
from django.db import models


class Event(models.Model):
    """
    Model to store events.

    It includes event title, description and data.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()

    def registration_count(self):
        """
        Returns the total number of registrations for this event.
        """
        return self.registrations.count()

    def __str__(self):
        return self.title


class Registration(models.Model):
    """
    Model to store event registrations.

    It includes registered user name and email.
    """
    event = models.ForeignKey(Event, related_name='registrations', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        unique_together = ('event', 'email')

    def __str__(self):
        return f"{self.name} - {self.event.title}"
