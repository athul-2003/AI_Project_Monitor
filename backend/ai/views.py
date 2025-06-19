# backend/ai/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from projects.models import Project, Task, Comment
from .ai_utils import get_project_insights

@staff_member_required
def project_insights_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if not request.user.is_superuser:
        return render(request, 'display/error.html', {'message': 'You do not have permission to view project insights.'}, status=403)
    
    # Get assigned developers (if you plan to support M2M later)
    assigned_developers = []
    if hasattr(project, 'assigned_developer') and project.assigned_developer:
        assigned_developers = [project.assigned_developer.username]
    elif hasattr(project, 'assigned_developers') and project.assigned_developers.exists():
        assigned_developers = [dev.username for dev in project.assigned_developers.all()]

    # Tasks overview
    tasks = project.tasks.all()
    task_summaries = []
    for task in tasks:
        dev_name = task.assigned_developer.username if task.assigned_developer else "Unassigned"
        task_summaries.append(f"🔹 {task.title} - {task.status} (Assigned to: {dev_name})")

    # Comments overview
    recent_comments = Comment.objects.filter(task__project=project).order_by('-created_at')[:5]
    comment_summaries = []
    for comment in recent_comments:
        comment_summaries.append(f"{comment.user.username}: {comment.content}")

    # Prepare data for LLM
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
    
    context = {
        'project': project,
        'summary': insights['summary'],
        'suggestions': insights['suggestions'],
    }
    
    return render(request, 'ai/project_insights.html', context)
