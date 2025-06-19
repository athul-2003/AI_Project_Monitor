# ai_suite/urls.py
from django.urls import path
from . import views
from .api_view import ai_suite_api_view

urlpatterns = [
    path('', views.ai_suite_view, name='ai_suite_view'),
    
    path('api/', ai_suite_api_view, name='ai-suite-api'), # for crewai api summary
]
