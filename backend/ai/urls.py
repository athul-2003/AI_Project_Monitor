# backend/ai/urls.py
from django.urls import path
from . import views
from .api_view import project_insights_api

urlpatterns = [
    path('insights/<int:project_id>/', views.project_insights_view, name='project_insights'),
    # api path
    path('api/project/<int:project_id>/insights/', project_insights_api, name='project-insights-api'),
]