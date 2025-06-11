# backend/ai/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('insights/<int:project_id>/', views.project_insights_view, name='project_insights'),
]