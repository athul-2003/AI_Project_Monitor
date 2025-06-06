from django import forms
from django.contrib.auth.models import User, Group
from projects.models import Project # Use the actual path to your Project model

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

     # Custom field to select a developer from the Developers group
    assigned_developer = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Developers'),
        required=False,
        empty_label="No Developer Assigned",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Managers'),
        required=True,
        # empty_label="Assign a Manager",
        label="Manager",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Project
        fields = ['name', 'description','user','assigned_developer','deadline','current_status','estimated_budget','current_budget',]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            # if field.name == 'description':
            #     field.widget.attrs.update({'rows': 4})
        # Only admins can edit the manager field
        if user and not user.is_superuser:
            self.fields.pop('user')
        