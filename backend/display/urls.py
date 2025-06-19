from django.urls import path
from . import views

app_name = 'display'

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Project-related
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/create/', views.project_create_view, name='project_create'),
    path('projects/<int:pk>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:pk>/update/', views.project_update_view, name='project_update'),
    path('projects/<int:pk>/delete/', views.project_delete_view, name='project_delete'),
    path('projects/<int:pk>/log/', views.project_log_view, name='project_log'),

    # Task-related
    path('projects/<int:pk>/tasks/create/', views.task_create, name='task_create'),  # Changed to 'tasks'
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    
    path('tasks/<int:task_id>/back-to-project/', views.back_to_project_from_task, name='back_to_project'),

    path('tasks/<int:pk>/update/', views.task_update_view, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete_view, name='task_delete'),
    path('tasks/my/', views.tasks_dashboard, name='tasks_dashboard'), 
    path('task/<int:task_id>/comment/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),


]
