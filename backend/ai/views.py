# backend/ai/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from projects.models import Project
from .ai_utils import get_project_insights

@staff_member_required
def project_insights_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if not request.user.is_superuser:
        return render(request, 'display/error.html', {'message': 'You do not have permission to view project insights.'}, status=403)
    
    # Extract data from the Django model into a dictionary
    assigned_developers = []
    if hasattr(project, 'assigned_developer') and project.assigned_developer:
        assigned_developers = [project.assigned_developer.username]
    elif hasattr(project, 'assigned_developers') and project.assigned_developers.exists():
        assigned_developers = [dev.username for dev in project.assigned_developers.all()]

    project_data = {
        "title": str(project.name),
        "description": str(project.description),
        "status": str(project.current_status),
        "deadline": str(project.deadline),
        "assigned_developers": assigned_developers,
        # "progress": str(project.progress_updates if hasattr(project, 'progress') and project.progress else "No progress reported"),
        "progress": str(project.progress_updates),
        # "issues": str(project.errors if hasattr(project, 'issues') and project.issues else "No issues reported")
         "issues": str(project.errors)
    }
    
    insights = get_project_insights(project_data)
    
    context = {
        'project': project,
        'summary': insights['summary'],
        'suggestions': insights['suggestions'],
    }
    
    return render(request, 'ai/project_insights.html', context)