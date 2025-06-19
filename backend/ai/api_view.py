# backend/ai/api_views.py
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from projects.models import Project, Comment
from .ai_utils import get_project_insights

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])  # Only admin
def project_insights_api(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    assigned_developers = []
    if hasattr(project, 'assigned_developer') and project.assigned_developer:
        assigned_developers = [project.assigned_developer.username]
    elif hasattr(project, 'assigned_developers') and project.assigned_developers.exists():
        assigned_developers = [dev.username for dev in project.assigned_developers.all()]
    
    tasks = project.tasks.all()
    task_summaries = [
        f"🔹 {task.title} - {task.status} (Assigned to: {task.assigned_developer.username if task.assigned_developer else 'Unassigned'})"
        for task in tasks
    ]
    
    recent_comments = Comment.objects.filter(task__project=project).order_by('-created_at')[:5]
    comment_summaries = [f"{comment.user.username}: {comment.content}" for comment in recent_comments]
    
    project_data = {
        "title": str(project.name),
        "description": str(project.description),
        "status": str(project.current_status),
        "deadline": str(project.deadline),
        "assigned_developers": assigned_developers,
        "progress": f"{len(tasks.filter(status='DONE'))} of {tasks.count()} tasks completed",
        "issues": " and ".join(set([task.title for task in tasks.filter(status='BLOCKED')])),
        "tasks": "\n".join(task_summaries) or "No tasks yet.",
        "comments": "\n".join(comment_summaries) or "No recent comments."
    }

    insights = get_project_insights(project_data)
    
    return Response({
        'project': project.name,
        'summary': insights['summary'],
        'suggestions': insights['suggestions'],
    }, status=status.HTTP_200_OK)
