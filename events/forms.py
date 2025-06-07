"""
Form for registration management.

Includes a user registration form with validation to prevent duplicate
registrations for the same event.
"""
from django import forms
from .models import Registration


class RegistrationForm(forms.ModelForm):
    """
    Form for creating and validating Registration instances.
    """
    class Meta:
        model = Registration
        fields = ['name', 'email']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and add Bootstrap form-control CSS class to all fields.
        """
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        """
        Validate that the email is not already registered for the given event.

        Raises:
            forms.ValidationError: If a registration with the same email
            already exists for the event.

        Returns:
            str: The cleaned email.
        """
        email = self.cleaned_data.get('email')
        if self.event and Registration.objects.filter(event=self.event, email=email).exists():
            raise forms.ValidationError("This email has already registered for this event.")
        return email
