from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate
from .models import Project, Category, Course, ProgrammingLanguage

class AssignUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=False), label="User")
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label="Project")


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProjectForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select all categories that apply"
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'categories']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if ',' in name:
            raise forms.ValidationError("Project name cannot contain commas.")
        return name


class CourseForm(forms.ModelForm):
    programming_languages = forms.ModelMultipleChoiceField(
        queryset=ProgrammingLanguage.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select all programming languages that apply"
    )

    class Meta:
        model = Course
        fields = ['name', 'description', 'level', 'programming_languages']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        help_text="Enter a strong password with at least 8 characters."
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Your current password is incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("The two password fields didn't match.")
            if len(new_password1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")

        return cleaned_data

    def save(self):
        password = self.cleaned_data.get('new_password1')
        self.user.set_password(password)
        self.user.save()
        return self.user


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(
        label="New Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.user.id).exists():
            raise forms.ValidationError("This email is already in use by another account.")
        return email

    def save(self):
        self.user.email = self.cleaned_data.get('email')
        self.user.save()
        return self.user


class ChangeUsernameForm(forms.Form):
    username = forms.CharField(
        label="New Username",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        max_length=150
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(id=self.user.id).exists():
            raise forms.ValidationError("This username is already taken.")
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        return username

    def save(self):
        self.user.username = self.cleaned_data.get('username')
        self.user.save()
        return self.user