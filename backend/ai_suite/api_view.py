# backend/ai/api_views.py
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status as drf_status

from django.db.models import Q
from collections import Counter

from projects.models import Project, Task
from .crew_ai_assistant import get_project_intelligence


STATUS_MAP = {
    "In Progress": ["In Progress", "IN-PROGRESS"],
    "On Hold": ["On Hold", "ON-HOLD"],
    "Completed": ["Completed", "COMPLETED"],
    "Delayed": ["Delayed", "delayed"],
}


def build_status_filter(selected_status):
    options = STATUS_MAP.get(selected_status, [])
    return Q(current_status__in=options)


def get_project_task_summary(projects):
    tasks = Task.objects.filter(project__in=projects).select_related('assigned_developer')
    if not tasks.exists():
        return None, "⚠️ No tasks found for selected project(s)."

    project_data = "\n".join([
        f"Name: {p.name}, Status: {p.current_status}, Budget: ₹{p.current_budget}/{p.estimated_budget}, Deadline: {p.deadline}"
        for p in projects
    ])
    task_data = [
        f"{t.title} - {t.status} - Assigned to: {t.assigned_developer.username if t.assigned_developer else 'Unassigned'}"
        for t in tasks
    ]
    dev_counter = Counter(t.assigned_developer.username for t in tasks if t.assigned_developer)
    developer_summary = "\n".join([f"{dev}: {count} tasks" for dev, count in dev_counter.items()])
    
    return {
        "project_data": project_data,
        "task_data": "\n".join(task_data),
        "developer_summary": developer_summary
    }, None


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def ai_suite_api_view(request):
    selected_status = request.GET.get('status', '')

    if not selected_status:
        return Response(
            {"error": "Please provide a status parameter in the query string."},
            status=drf_status.HTTP_400_BAD_REQUEST
        )

    status_filter = build_status_filter(selected_status)
    projects = Project.objects.filter(status_filter)

    if not projects.exists():
        return Response(
            {"message": "⚠️ No projects found for selected status."},
            status=drf_status.HTTP_404_NOT_FOUND
        )

    summary, error_msg = get_project_task_summary(projects)
    if error_msg:
        return Response({"message": error_msg}, status=drf_status.HTTP_404_NOT_FOUND)

    ai_output = get_project_intelligence(
        project_data=summary["project_data"],
        task_data=summary["task_data"],
        developer_summary=summary["developer_summary"],
    )

    return Response({
        "ai_output": ai_output,
        "selected_status": selected_status
    }, status=drf_status.HTTP_200_OK)
