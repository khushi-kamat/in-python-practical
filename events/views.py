"""
View functions for event management operations such as listing,
user registration, and confirmation.
"""
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.utils.timezone import now
from events.forms import RegistrationForm
from events.models import Event

logger = logging.getLogger(__name__)


def event_list(request):
    """
    Display a list of all events with optional filtering and search.
    Supports filtering past or upcoming events, and searching by title.
    Returns JSON for AJAX requests, otherwise renders the event list page.
    """
    filter_val = request.GET.get('filter')
    search_val = request.GET.get('search', '').strip()

    events = Event.objects.all()
    if filter_val == 'past':
        events = events.filter(date__lt=now()).order_by('-date')
    else:
        events = events.filter(date__gte=now()).order_by('date')
    if search_val:
        events = events.filter(title__icontains=search_val)
    events = events.annotate(registration_count=Count('registrations'))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        events_data = list(events.values('id', 'title', 'date', 'registration_count'))
        return JsonResponse({'events': events_data})

    context = {'events': events}
    return render(request, 'events/events.html', context)


def event_detail(request, event_id):
    """
    Display details of a specific event. Shows registration form if the event
    is upcoming, otherwise marks it as past. Raises 404 if event not found.
    """
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist as exc:
        logger.info(f"No event found with id: {event_id}")
        raise Http404("Event not found") from exc
    is_past = event.date < now()
    event_form = RegistrationForm() if not is_past else None
    context = {'event': event, 'event_form': event_form, 'is_past': is_past}
    return render(request, 'events/event_detail.html', context)


def register(request, event_id):
    """
    Handle user registration for a specific event via POST. Validates the
    registration form and saves a new registration. Redirects to confirmation
    page upon success. Raises 404 if event not found.
    """
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist as exc:
        logger.info(f"No event found with id: {event_id}")
        raise Http404("Event not found") from exc
    if request.method == 'POST':
        event_form = RegistrationForm(request.POST, event=event)
        if event_form.is_valid():
            registration = event_form.save(commit=False)
            registration.event = event
            registration.save()
            try:
                send_mail(
                    'Event Registration Confirmation',
                    f'Thank you {registration.name} for registering for {event.title}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [registration.email],
                    fail_silently=True,
                )
                logger.info(f"Confirmation email sent to {registration.email}")
            except Exception as exc:    # pylint: disable=broad-exception-caught
                logger.info(f"Failed to send confirmation email to {registration.email}: {exc}")
            messages.success(request, "You have registered successfully!")
            return redirect('events:confirmation')
    context = {'event': event, 'event_form': event_form}
    return render(request, 'events/event_detail.html', context)


def confirmation(request):
    """
    Render the registration confirmation page.
    """
    return render(request, 'events/confirmation.html')


def custom_404_view(request, exception):    # pylint: disable=unused-argument
    """
    Render a custom 404 error page.
    """
    return render(request, 'events/404.html', status=404)
