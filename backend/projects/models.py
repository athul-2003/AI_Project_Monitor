from django.db import models
from django.contrib.auth.models import User


CURRENT_STATUS = [
    ("ON-HOLD", "On Hold"),
    ("COMPLETED", "Completed"),
    ("IN-PROGRESS", "In Progress"),
]

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 🔗 Link project to user
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
