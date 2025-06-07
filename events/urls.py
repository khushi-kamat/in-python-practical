"""
URLs for events package.
"""
from django.urls import path
from events import views


app_name = 'events'
urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/register/', views.register, name='register'),
    path('confirmation/', views.confirmation, name='confirmation'),
]
