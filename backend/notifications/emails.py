from django.core.mail import send_mail
from django.conf import settings


# function to handle sending emails
def handle_project_update_emails(old_dev, updated_project, request_user, is_developer):
    new_dev = updated_project.assigned_developer

    # Case 1: Developer changed
    if new_dev and new_dev != old_dev:
        send_project_assignment_email(new_dev, updated_project, request_user)

    # Case 2: Developer same and manager updated
    elif new_dev == old_dev and new_dev and not is_developer:
        send_project_update_email(new_dev, updated_project, request_user)

    # Case 3: Developer updated project → notify manager
    if is_developer:
        manager = updated_project.user
        send_dev_project_update_email(manager, updated_project, request_user)


# project assignment email to developer
def send_project_assignment_email(user, project, assigned_by):
    """
    Sends an email to the assigned developer about a new project.
    """
    if not user.email:
        return

    subject = 'New Project Assigned to You'
    message = f"""
Hi {user.first_name or user.username},

You have been assigned a new project.

📌 Project Name: {project.name}
📅 Deadline: {project.deadline.strftime('%d %B %Y')}
Assigned By: {assigned_by.get_full_name() or assigned_by.username}

Please log in to the system to see more details.

Regards,
Project Management System
"""

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # From email
            [user.email],
            fail_silently=False,
        )

        print(f"✅ Email sent to {user.email}")

    except Exception as e:
        print(f"❌ Failed to send email to {user.email}: {e}")


# project update email to developer
def send_project_update_email(user, project, updated_by):
    """
    Sends an email to the assigned developer about an update in project.
    """

    if not user.email:
        return

    subject = 'Update in Project'
    message = f"""
Hi {user.first_name or user.username},

There has been an update in your project.

📌 Project Name: {project.name}
📅 Deadline: {project.deadline.strftime('%d %B %Y')}
Updated By: {updated_by.username}

Please log in to the system to see more details.

Regards,
Project Management System
"""

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # From email
            [user.email],
            fail_silently=False,
        )

        print(f"✅ Email sent to {user.email}")

    except Exception as e:
        print(f"❌ Failed to send email to {user.email}: {e}")


# project update email to manager
def send_dev_project_update_email(manager, project, updated_by):
    if not manager.email:
        return

    subject = 'Update in Your Project by Developer'
    message = f"""
Hi {manager.first_name or manager.username},

The developer has updated the project you're managing.

📌 Project Name: {project.name}
📅 Deadline: {project.deadline.strftime('%d %B %Y')}
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
        