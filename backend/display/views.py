from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProjectForm , TaskForm, CommentForm
from projects.models import Project, Task, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from notifications.emails import send_task_assignment_email, handle_task_update_emails




def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('display:login')
    else:
        form = RegisterForm()
    return render(request, 'display/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('display:project_list')
            else:
                return render(request, 'display/login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = LoginForm()
    return render(request, 'display/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('display:login')


@login_required
def project_create_view(request):
    is_developer = request.user.groups.filter(name='Developers').exists()
    if is_developer:
        messages.error(request, "You do not have permission to create projects.")
        return redirect('display:project_list')

    if request.method == 'POST':
        form = ProjectForm(request.POST, current_user=request.user)
        if form.is_valid():
            project = form.save(commit=False)

            # If not admin, set the manager to the logged-in user
            if not request.user.is_superuser:
                project.user = request.user

            project.save()

            messages.success(request, f"Project '{project.name}' has been created successfully.")
            return redirect('display:project_list')
    else:
        form = ProjectForm(current_user=request.user)

    return render(request, 'display/project_create.html', {'form': form})


@login_required
def project_list_view(request):
    # Check user roles
    is_admin = request.user.is_superuser
    is_developer = request.user.groups.filter(name='Developers').exists()
    
    # Base queryset based on user role
    if is_admin:
        # Admin sees all projects
        projects = Project.objects.all()
    elif is_developer:
         # Get all projects where the user has tasks
        projects = Project.objects.filter(tasks__assigned_developer=request.user).distinct()
    else:
        # Managers see only their created projects
        projects = Project.objects.filter(user=request.user)

    # Apply status filter if provided
    status = request.GET.get('status')
    if status in ["ON-HOLD", "On Hold", "COMPLETED", "Completed", "IN-PROGRESS", "In Progress", 'delayed', 'Delayed']:
        projects = projects.filter(current_status=status)
    
    # Order projects by created_at
    projects = projects.order_by('-created_at')

    # Pagination
    page_number = request.GET.get('page')
    paginator = Paginator(projects, 6)  # Show 6 projects per page
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Status choices for the filter dropdown
    status_choices = [
    ("ON-HOLD", "On Hold"),
    ("COMPLETED", "Completed"),
    ("IN-PROGRESS", "In Progress"),
    ('delayed', 'Delayed'),
]

    context = {
        'projects': projects,
        'is_admin': is_admin,
        'is_developer': is_developer,
        'page_obj': page_obj,
        'status_choices': status_choices,
        'selected_status': status,
    }
    return render(request, 'display/project_list.html', context)


# @login_required
# def project_detail_view(request, pk):
#     # Check user roles
#     is_admin = request.user.is_superuser
#     is_developer = request.user.groups.filter(name='Developers').exists()
    
#     if is_admin:
#         # Admin can view any project
#         project = get_object_or_404(Project, pk=pk, )
#     elif is_developer:
#         # Get all projects where the developer has tasks assigned
#         project = get_object_or_404(Project, pk=pk, tasks__assigned_developer=request.user)
#     else:
#         # Managers can only view their own projects
#         project = get_object_or_404(Project, pk=pk, user=request.user)

#     # Get all unique developers assigned to tasks in this project
#     developers = User.objects.filter(id__in=project.tasks.values_list('assigned_developer', flat=True)
#     ).distinct()

#     context = {'project': project,
#     'is_admin': is_admin,
#     'is_developer': is_developer,
#     'developers': developers}
    
#     return render(request, 'display/project_detail.html', context)



@login_required
def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    is_admin = user.groups.filter(name='Admin').exists()
    is_developer = user.groups.filter(name='Developers').exists()

    # Get all developers assigned to this project
    developers = User.objects.filter(id__in=project.tasks.values_list('assigned_developer', flat=True)
    ).distinct()

    # Create a list of developers and their tasks
    dev_task_list = []
    for dev in developers:
        tasks = Task.objects.filter(project=project, assigned_developer=dev)
        dev_task_list.append({
            'developer': dev,
            'tasks': tasks
        })

    return render(request, 'display/project_detail.html', {
        'project': project,
        'is_admin': is_admin,
        'is_developer': is_developer,
        'dev_task_list': dev_task_list,
    })



@login_required
def project_log_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Get all tasks for the project, also fetch assigned_developer for optimization
    tasks = Task.objects.filter(project=project).select_related('assigned_developer')

    # Add related comments to each task (fetch user details for each comment)
    for task in tasks:
        task.comment_list = Comment.objects.filter(task=task).select_related('user')

    return render(request, 'display/project_log.html', {
        'project': project,
        'tasks': tasks,
    })


@login_required
def project_update_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_admin = request.user.is_superuser
    is_manager = request.user.groups.filter(name='Managers').exists()
    is_developer = request.user.groups.filter(name='Developers').exists()

    # Restrict non-admin managers to only their own projects
    if is_manager and not is_admin and project.user != request.user:
        messages.error(request, "You can only update your own projects.")
        return redirect('display:project_list')

    mode = 'developer' if is_developer else 'full'


    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project, current_user=request.user, mode=mode)
        if form.is_valid():
            updated_project = form.save(commit=False)
            updated_project.save()
            form.save()

            # Send notification emails to all developers on the project
            # handle_project_update_emails(old_assigned_devs, updated_project, request.user, is_developer)

            messages.success(request, f"Project '{project.name}' has been updated successfully.")
            return redirect('display:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project, current_user=request.user, mode=mode)

    return render(request, 'display/project_update.html', {
        'form': form,
        'project': project,
        'is_admin': is_admin,
        'is_developer': is_developer
    })


@login_required
def project_delete_view(request, pk):
    # Check user roles
    is_admin = request.user.is_superuser
    is_developer = request.user.groups.filter(name='Developers').exists()
    
    if is_developer:
        messages.error(request, "You do not have permission to delete projects.")
        return redirect('display:project_list')
    
    if is_admin:
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f"Project '{project_name}' has been deleted successfully.")
        return redirect('display:project_list')
    return render(request, 'display/project_delete_confirm.html', {'project': project, 'is_admin': is_admin})


# tasks and comments

def check_manager_access(user, project):
    return user.is_superuser or (user.groups.filter(name='Managers').exists() and project.user == user)

def check_developer_access(user, project):
    return user.groups.filter(name='Developers').exists() and project.assigned_developer == user

@login_required
def task_create(request, pk):
    project = get_object_or_404(Project, id=pk)
    
    if not check_manager_access(request.user, project):
        messages.error(request, "You don't have permission to create tasks for this project.")
        return redirect('display:project_detail', pk=project.pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, current_user=request.user, mode='full')
        if form.is_valid():
            task = form.save(commit=False)
            assigned_by = request.user # get who assigned project
            task.project = project
            task.save()

            # Send email to the newly assigned developer (if any) when task is created
            if task.assigned_developer and task.assigned_developer.email:
                send_task_assignment_email(task.assigned_developer, project, task, assigned_by)

            messages.success(request, f"Task '{task.title}' created successfully.")
            return redirect('display:project_detail', pk=project.pk)
    else:
        form = TaskForm(current_user=request.user, mode='full')
    
    return render(request, 'display/task_form.html', {
        'form': form,
        'project': project,
        'title': 'Create Task',

    })


# tasks dashboard for : managers who assign tasks and developers who are assigned with tasks
@login_required
def tasks_dashboard(request):
    user = request.user
    is_developer = user.groups.filter(name='Developers').exists()
    is_manager = user.groups.filter(name='Managers').exists()
    
    if is_developer:
        # Developers see only their assigned tasks
        tasks = Task.objects.filter(assigned_developer=user).select_related('project')
    elif is_manager:
        # Managers see all tasks in their own projects
        tasks = Task.objects.filter(project__user=user).select_related('project')
    else:
        # Default: show nothing or everything based on your system's permission model
        tasks = Task.objects.none()


    # Order tasks by created_at
    tasks = tasks.order_by('-created_at')

    # Pagination logic
    paginator = Paginator(tasks, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'tasks': page_obj.object_list,
        'is_developer': is_developer,
        'is_manager': is_manager,
    }
    return render(request, 'display/tasks_dashboard.html', context)



@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    comments = Comment.objects.filter(task=task, parent=None).select_related('user').prefetch_related('replies')
    is_manager = request.user.groups.filter(name="Managers").exists()
    is_developer = request.user.groups.filter(name="Developers").exists()
    can_comment = (task.assigned_developer == request.user) or is_manager
    comment_form = CommentForm()

    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
        'is_manager': is_manager,
        'is_developer': is_developer,
        'request': request,
        'can_comment': can_comment
    }
    return render(request, 'display/task_detail.html', context)


@login_required
def back_to_project_from_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    return redirect('display:project_detail', pk=task.project.pk)


@login_required
def task_update_view(request,pk):

    task = get_object_or_404(Task, pk=pk)
    user = request.user
    is_admin = user.is_superuser
    is_manager = user.groups.filter(name='Managers').exists()
    is_developer = user.groups.filter(name='Developers').exists()

    # Permission: Managers can edit only tasks under their projects
    if is_manager and not is_admin and task.project.user != user:
        messages.error(request, "You can only edit tasks in your own projects.")
        return redirect('display:project_list')

    # Permission: Developers can only edit if assigned
    if is_developer:
        if task.assigned_developer != user:
            messages.error(request, "You are not assigned to this task.")
            return redirect('display:tasks_dashboard')
        mode = 'developer'
    else:
        mode = 'full'

    if request.method == 'POST':
        old_dev = task.assigned_developer  # Store old developer

        form = TaskForm(request.POST, instance=task, current_user=user, mode=mode)
        if form.is_valid():
            updated_task = form.save()
            
            # Handles both developer and manager email updates
            handle_task_update_emails(old_dev, updated_task, request_user=request.user)

        messages.success(request, f"Task '{updated_task.title}' has been updated successfully.")
        return redirect('display:task_detail', pk=updated_task.pk)
    else:
        form = TaskForm(instance=task, current_user=user, mode=mode)

    return render(request, 'display/task_update.html', {
        'form': form,
        'task': task,
        'is_developer': is_developer
    })

@login_required
def task_delete_view(request, pk):
    user = request.user
    is_admin = user.is_superuser
    is_developer = user.groups.filter(name='Developers').exists()

    # Prevent developers from deleting tasks
    if is_developer:
        messages.error(request, "You do not have permission to delete a task.")
        return redirect('display:tasks_dashboard')

    # Get the task: Admins can delete anything; Managers can only delete their own project tasks
    if is_admin:
        task = get_object_or_404(Task, pk=pk)
    else:
        task = get_object_or_404(Task, pk=pk, project__user=user)

    if request.method == 'POST':
        task_name = task.title
        task.delete()
        messages.success(request, f"Task '{task_name}' has been deleted successfully.")
        return redirect('display:tasks_dashboard')  # Or a manager dashboard, if you have one

    return render(request, 'display/task_delete_confirm.html', {
        'task': task,
        'is_admin': is_admin
    })


@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id')
            parent_comment = Comment.objects.filter(id=parent_id).first() if parent_id else None

            Comment.objects.create(
                task=task,
                user=request.user,
                content=form.cleaned_data['content'],
                parent=parent_comment
            )
            messages.success(request, "Comment posted.")
            return redirect('display:task_detail', pk=task_id)
    else:
        form = CommentForm()

    return redirect('display:task_detail', pk=task_id)



@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        messages.error(request, "You are not allowed to edit this comment.")
        return redirect('display:task_detail', pk=comment.task.pk)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated.")
            return redirect('display:task_detail', pk=comment.task.pk)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'display/edit_comment.html', {'form': form, 'comment': comment})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        messages.error(request, "You are not authorized to delete this comment.")
        return redirect('display:task_detail', pk=comment.task.pk)

    task_id = comment.task.pk
    comment.delete()
    messages.success(request, "Comment deleted.")
    return redirect('display:task_detail', pk=task_id)





