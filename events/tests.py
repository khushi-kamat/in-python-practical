"""
Tests for the RegistrationForm in events package.
"""
import logging
from html.parser import HTMLParser
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now, timedelta
from events.forms import RegistrationForm
from events.models import Event, Registration

logger = logging.getLogger(__name__)


class RegistrationFormTests(TestCase):
    """Test cases for the RegistrationForm validation logic."""

    def setUp(self):
        """Create events for test cases."""
        self.event1 = Event.objects.create(
            title="Event One",
            description="First Event",
            date=now() + timedelta(days=1)
        )
        self.event2 = Event.objects.create(
            title="Event Two",
            description="Second Event",
            date=now() + timedelta(days=2)
        )

    def test_registration_form_valid_data(self):
        """Test that the form is valid with unique email for event."""
        form_data = {'name': 'Test User', 'email': 'testuser@example.com'}
        form = RegistrationForm(data=form_data, event=self.event1)
        self.assertTrue(form.is_valid())

    def test_registration_form_duplicate_email_same_event(self):
        """Test that form is invalid if email already registered for same event."""
        Registration.objects.create(
            name='Test User',
            email='testuser@example.com',
            event=self.event1
        )

        form_data = {'name': 'Test User', 'email': 'testuser@example.com'}
        form = RegistrationForm(data=form_data, event=self.event1)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(
            form.errors['email'],
            ["This email has already registered for this event."]
        )

    def test_registration_form_duplicate_email_different_event(self):
        """Test that form is valid if same email is used for a different event."""
        Registration.objects.create(
            name='Test User',
            email='testuser@example.com',
            event=self.event1
        )
        form_data = {'name': 'Test User', 'email': 'testuser@example.com'}
        form = RegistrationForm(data=form_data, event=self.event2)
        self.assertTrue(form.is_valid())


class EventListViewTests(TestCase):
    """
    Test cases for the event list view, including filtering, searching,
    and AJAX responses.
    """

    def setUp(self):
        """Create client, URL, and events for testing event list view."""
        self.client = Client()
        self.url = reverse('events:event_list')
        Event.objects.create(title="Past Event", date=now() - timedelta(days=1))
        Event.objects.create(title="Upcoming Event", date=now() + timedelta(days=1))

    def extract_titles(self, html):
        """
        Parse the HTML content and extract event titles from the first <td>
        of each table row in the events list table.
        """
        class Parser(HTMLParser):
            """HTML parser to extract event titles from table cells."""
            def __init__(self):
                super().__init__()
                self.in_td = False
                self.td_count = 0
                self.titles = []
                self.capture = False
            def handle_starttag(self, tag, attrs):
                if tag == 'td':
                    self.in_td = True
                    self.td_count += 1
                    if self.td_count == 1:
                        self.capture = True
            def handle_endtag(self, tag):
                if tag == 'td':
                    self.in_td = False
                    self.capture = False
                if tag == 'tr':
                    self.td_count = 0
            def handle_data(self, data):
                if self.capture:
                    self.titles.append(data.strip())
        parser = Parser()
        parser.feed(html)
        return parser.titles

    def test_event_list_default_shows_upcoming(self):
        """Verify the default event list shows only upcoming events."""
        response = self.client.get(self.url)
        titles = self.extract_titles(response.content.decode())
        self.assertIn("Upcoming Event", titles)
        self.assertNotIn("Past Event", titles)

    def test_event_list_filter_past(self):
        """Verify filtering by 'past' shows only past events."""
        response = self.client.get(self.url + '?filter=past')
        titles = self.extract_titles(response.content.decode())
        self.assertIn("Past Event", titles)
        self.assertNotIn("Upcoming Event", titles)

    def test_event_list_search(self):
        """Verify search filters events by title substring."""
        response = self.client.get(self.url + '?search=upcoming')
        titles = self.extract_titles(response.content.decode())
        self.assertIn("Upcoming Event", titles)
        self.assertNotIn("Past Event", titles)

    def test_event_list_ajax_returns_json(self):
        """Verify AJAX request returns JSON content with events."""
        response = self.client.get(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')


class EventDetailViewTests(TestCase):
    """Test cases for event detail page behavior."""

    def setUp(self):
        """Create upcoming and past events for detail view tests."""
        self.client = Client()
        self.upcoming_event = Event.objects.create(title="Event", date=now() + timedelta(days=1))
        self.past_event = Event.objects.create(title="Past", date=now() - timedelta(days=1))

    def test_event_detail_valid(self):
        """Test that event detail page loads for valid upcoming event."""
        url = reverse('events:event_detail', args=[self.upcoming_event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('event_form', response.context)

    def test_event_detail_past_event_hides_form(self):
        """Test that registration form is hidden for past events."""
        url = reverse('events:event_detail', args=[self.past_event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['event_form'])

    def test_event_detail_invalid_event_404(self):
        """Test that requesting invalid event ID returns 404."""
        response = self.client.get(reverse('events:event_detail', args=[999]))
        self.assertEqual(response.status_code, 404)
        logger.info("Expected 404 received for invalid event detail request.")


class EventRegisterViewTests(TestCase):
    """Test cases for event registration functionality."""

    def setUp(self):
        """Create client and an upcoming event for registration tests."""
        self.client = Client()
        self.event = Event.objects.create(title="Event", date=now() + timedelta(days=1))
        self.url = reverse('events:register', args=[self.event.id])

    def test_register_valid_post(self):
        """Test successful registration with valid POST data redirects to confirmation."""
        data = {'name': 'Test User', 'email': 'testuser@example.com'}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('events:confirmation'))
        self.assertTrue(Registration.objects.filter(email='testuser@example.com').exists())

    def test_register_invalid_email_duplicate(self):
        """Test registration fails with duplicate email for same event."""
        Registration.objects.create(event=self.event, name='Test User',
            email='testuser@example.com')
        data = {'name': 'Test User', 'email': 'testuser@example.com'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['event_form']
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_register_invalid_event_404(self):
        """Test registration POST on invalid event ID returns 404."""
        response = self.client.post(reverse('events:register', args=[999]),
            {'name': 'Test User', 'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, 404)
        logger.info("Expected 404 received for invalid event register request.")


class ConfirmationViewTests(TestCase):
    """Test case for confirmation page rendering."""

    def test_confirmation_page_renders(self):
        """Test that the confirmation page renders successfully."""
        response = Client().get(reverse('events:confirmation'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/confirmation.html')
