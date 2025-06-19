from django.contrib import admin
from .models import Project, Task , Comment

# Register your models here.

# admin.site.register(Project)
# admin.site.register(Task)
# admin.site.register(Comment)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','deadline', 'current_status')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_developer', 'status', 'due_date')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
