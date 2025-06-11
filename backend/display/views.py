from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProjectForm
from projects.models import Project
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from notifications.emails import send_project_assignment_email, handle_project_update_emails



# Existing views for register, login, logout remain unchanged
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
            
            assigned_by = request.user # get who assigned project

            # If not admin, set the manager to the logged-in user
            if not request.user.is_superuser:
                project.user = request.user

            project.save()
            form.save_m2m()  # for any M2M fields

            # ✅ Send email using utility function
            if project.assigned_developer:
                send_project_assignment_email(project.assigned_developer, project, assigned_by)

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
    
    if is_admin:
        # Admin sees all projects
        projects = Project.objects.all().order_by('-created_at')
        paginator = Paginator(projects, 6)  # Show 6 projects per page
    elif is_developer:
        # Developers see only projects assigned to them
        projects = Project.objects.filter(assigned_developer=request.user)
        paginator = Paginator(projects, 6)  # Show 6 projects per page
    else:
        # Managers see only their created projects
        projects = Project.objects.filter(user=request.user)
        paginator = Paginator(projects, 6)  # Show 6 projects per page

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {'projects': projects, 'is_admin': is_admin, 'is_developer': is_developer, 'page_obj': page_obj}
    return render(request, 'display/project_list.html', context)

@login_required
def project_detail_view(request, pk):
    # Check user roles
    is_admin = request.user.is_superuser
    is_developer = request.user.groups.filter(name='Developers').exists()
    
    if is_admin:
        # Admin can view any project
        project = get_object_or_404(Project, pk=pk, )
    elif is_developer:
        # Developers can only view projects assigned to them
        project = get_object_or_404(Project, pk=pk, assigned_developer=request.user)
    else:
        # Managers can only view their own projects
        project = get_object_or_404(Project, pk=pk, user=request.user)
    
    return render(request, 'display/project_detail.html', {'project': project, 'is_admin': is_admin, 'is_developer': is_developer})


@login_required
def project_update_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_admin = request.user.is_superuser
    is_manager = request.user.groups.filter(name='Managers').exists()
    is_developer = request.user.groups.filter(name='Developers').exists()

    # Restrict non-admin managers to only their projects
    if is_manager and not is_admin and project.user != request.user:
        messages.error(request, "You can only update your assigned projects.")
        return redirect('display:project_list')

    # Developer can update only certain fields
    if is_developer:
        mode = 'developer'
    else:
        mode = 'full'

    old_assigned_dev = project.assigned_developer  # 🔁 Store current developer before form save

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project, current_user=request.user, mode=mode)
        if form.is_valid():
            updated_project = form.save(commit=False)
            updated_project.save()
            form.save()

            # 📤 Refactored email handling
            handle_project_update_emails(old_assigned_dev, updated_project, request.user, is_developer)

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