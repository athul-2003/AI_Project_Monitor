from django import forms
from django.contrib.auth.models import User, Group
from projects.models import Project, Task, Comment

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username','password','email','first_name','last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ProjectForm(forms.ModelForm):
    deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    user = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Managers'),
        required=True,
        label="Manager",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Project
        fields = ['name', 'description','user','deadline','current_status','estimated_budget','current_budget']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        mode = kwargs.pop('mode', 'full')  # full or developer
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Only admins can edit the manager field
        if user and not user.is_superuser:
            self.fields.pop('user')



# tasks and comments

class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    assigned_developer = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Developers'),
        required=False,
        empty_label="No Developer Assigned",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_developer', 'due_date', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        mode = kwargs.pop('mode', 'full')  # full or developer
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Restrict fields for developers
        if mode == 'developer':
            allowed = ['status']  # <-- Only allow status for developer
            for field_name in list(self.fields.keys()):
                if field_name not in allowed:
                    self.fields.pop(field_name)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Add a comment...'
        })