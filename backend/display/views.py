from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm, ProjectForm
from projects.models import Project
from django.contrib import messages

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
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user  
            project.save()
            return redirect('display:project_list')
    else:
        form = ProjectForm()
    return render(request, 'display/project_create.html', {'form': form})

# @login_required
# def project_list_view(request):
#     projects = Project.objects.filter(user=request.user)
#     return render(request, 'display/project_list.html', {'projects': projects})

# @login_required
# def project_detail_view(request, pk):
#     project = get_object_or_404(Project, pk=pk, user=request.user)
#     return render(request, 'display/project_detail.html', {'project' : project})

@login_required
def project_list_view(request):
    # Check if user is a superuser (admin)
    is_admin = request.user.is_superuser
    if is_admin:
        # Admin sees all projects in the company
        projects = Project.objects.all()
    else:
        # Regular users see only their projects
        projects = Project.objects.filter(user=request.user)
    return render(request, 'display/project_list.html', {'projects': projects, 'is_admin': is_admin})

@login_required
def project_detail_view(request, pk):
    # Check if user is a superuser (admin)
    is_admin = request.user.is_superuser
    if is_admin:
        # Admin can view any project
        project = get_object_or_404(Project, pk=pk)
    else:
        # Regular users can only view their own projects
        project = get_object_or_404(Project, pk=pk, user=request.user)
    return render(request, 'display/project_detail.html', {'project': project, 'is_admin': is_admin,})

@login_required
def project_update_view(request, pk):
    is_admin = request.user.is_superuser
    if is_admin:
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('display:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'display/project_update.html', {'form': form, 'project': project, 'is_admin': is_admin})


@login_required
def project_delete_view(request, pk):
    is_admin = request.user.is_superuser
    if is_admin:
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == 'POST':
        project_name = project.name  #to store name for message
        project.delete()
        messages.success(request, f"Project '{project_name}' has been deleted successfully.")
        return redirect('display:project_list')
    # If GET request, render a confirmation page
    return render(request, 'display/project_delete_confirm.html', {'project': project, 'is_admin': is_admin})



