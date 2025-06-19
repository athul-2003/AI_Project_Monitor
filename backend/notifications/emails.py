from django.core.mail import send_mail
from django.conf import settings


def handle_task_update_emails(old_dev, task, request_user):
    new_dev = task.assigned_developer

    # Skip if no developer
    if not new_dev or not new_dev.email:
        return

    # Developer assigned or reassigned
    if new_dev != old_dev:
        send_task_update_email(new_dev, task.project, task, assigned_by=request_user)

    # Notify manager if the updater is a developer
    elif request_user.groups.filter(name='Developers').exists():
        manager = task.project.user
        send_dev_task_update_email(manager, task.project, task, updated_by=request_user)
    else:
        send_task_update_email(old_dev, task.project, task, assigned_by=request_user)


# task assignment email to dev
def send_task_assignment_email(user, project, task, assigned_by):
    """
    Sends an email to the newly assigned developer about a new task.
    """
    if not user.email:
        return

    subject = '📝 New Task Assigned to You'
    message = f"""
Hi {user.first_name or user.username},

You have been assigned a new task.

📌 Project Name: {project.name}
⚙️ Task: {task.title}
📅 Task Deadline: {task.due_date.strftime('%d %B %Y')}
Assigned By: {assigned_by.username}

Please log in to the system to see more details.

Regards,
Project Management System
"""

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        print(f"✅ Email sent to {user.email}")
    except Exception as e:
        print(f"❌ Failed to send email to {user.email}: {e}")


# task update email to developer
def send_task_update_email(developer, project, task, assigned_by):
    subject = "🛠️ Task Updated"

    message = f"""
Hi {developer.first_name or developer.username},

A task assigned to you has been updated.

📌 Project: {project.name}
⚙️ Task: {task.title}
📝 Updated By: {assigned_by.username}

Please login to view the latest details.

Regards,  
Project Management System
"""

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [developer.email],
            fail_silently=False,
        )
        print(f"✅ Email sent to {developer.email}")
    except Exception as e:
        print(f"❌ Failed to send email to {developer.email}: {e}")


# task update email to manager 
def send_dev_task_update_email(manager, project, task, updated_by):
    if not manager.email:
        return

    subject = '🛠️ Task Update in Your Project by Developer'
    message = f"""
Hi {manager.first_name or manager.username},

The developer has updated the task you assigned.

📌 Project Name: {project.name}
⚙️ Task: {task.title}
Updated By: {updated_by.username}

Please log in to the system to review the update.

Regards,
Project Management System
"""

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [manager.email],
            fail_silently=False,
        )
        print(f"✅ Email sent to {manager.email}")
    except Exception as e:
        print(f"❌ Failed to send email to {manager.email}: {e}")
        