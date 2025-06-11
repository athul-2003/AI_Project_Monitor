from django.db import models
from django.contrib.auth.models import User


CURRENT_STATUS = [
    ("ON-HOLD", "On Hold"),
    ("COMPLETED", "Completed"),
    ("IN-PROGRESS", "In Progress"),
    ('delayed', 'Delayed'),
]

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_projects")  # 🔗 Link project to user
    assigned_developer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_projects')  # Developer assigned to it
    name = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateField()
    current_status = models.CharField(
        max_length=100,
        choices=CURRENT_STATUS,
        default="IN-PROGRESS",
    )
    estimated_budget = models.FloatField()
    current_budget = models.FloatField()
    progress_updates = models.TextField(blank=True, help_text="Latest updates on project progress.")
    errors = models.TextField(blank=True, help_text="Any errors, blockers, or issues encountered.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
