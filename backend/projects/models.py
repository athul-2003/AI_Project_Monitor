from django.db import models
from django.contrib.auth.models import User


CURRENT_STATUS = [
    ("ON-HOLD", "On Hold"),
    ("COMPLETED", "Completed"),
    ("IN-PROGRESS", "In Progress"),
    ('delayed', 'Delayed'),
]

TASK_STATUS = [
    ('TODO', 'To Do'),
    ('IN_PROGRESS', 'In Progress'),
    ('DONE', 'Done'),
    ('BLOCKED', 'Blocked'),
]

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_projects")  # 🔗 Link project to user
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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned_developer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tasks'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS,
        default='TODO',
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.project.name})"


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"

