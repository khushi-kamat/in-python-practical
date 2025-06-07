# 🗓️ Event Registration Platform
A simple Django-based platform for managing events, allowing users to view, search, filter, and register for events.

## Features
- View Upcoming Events with registered user count
- User Registration for an Event
- Send Confirmation Email on Successful Registration.
- Search and Filter for Past/Upcoming events.

## Functionality Overview
1. **List Upcoming Events**  
   - Displays title, date, and total number of registrations per event  
   - Supports filtering (past/upcoming) and searching by title  

2. **Event Detail Page**  
   - Shows event details  
   - Displays a registration form if the event is upcoming  

3. **Registration Form**  
   - Collects name and email  
   - Validates uniqueness of email per event  
   - On success: saves registration, sends confirmation email, and redirects to confirmation page

4. **Confirmation Page**  
   - Displays a thank-you message after successful registration

5. **Error Handling**
   - Custom 404 page for invalid event access.

## Test Coverage
- Unit tests covered:
  - Form validation (valid, duplicate checks)
  - Views (list, detail, registration, confirmation)
  - AJAX and search/filter behaviors

## Setup Instructions
- Create a Python 3.13 virtual environment
- Install dependencies: ```pip install -r requirements.txt```
- Run migrations for apps: ```python manage.py migrate```
- Collect static files: ```python manage.py collectstatic```
- Runserver: ```python manage.py runserver```
- Configure SMTP for registration confirmation email. Create a `.env` file in the project root and add the following variables:
  `EMAIL_HOST_USER=addhost`<br>
  `EMAIL_HOST_PASSWORD=addpassword`<br>
  `DEFAULT_FROM_EMAIL=addemail`
