from django import forms
from django.contrib.auth.forms import User
from django.contrib.auth import authenticate
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from .models import Category
from .models import Post

class ContactForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=100,
        required=True,
    )
    email = forms.EmailField(
        label="Email",
        max_length=100,
        required=True,
        validators=[EmailValidator(message="Please enter a valid email address")],
    )
    message = forms.CharField(
        required=True,
    )

class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        label="Username",
        max_length=100,
        required=True,
    )
    email = forms.EmailField(
        label="Email",
        max_length=100,
        required=True,
        validators=[EmailValidator(message="Please enter a valid email address")],
    )
    password = forms.CharField(
        label="Password",
        min_length=8,
        required=True,
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=100,
        required=True,
    )
    password = forms.CharField(
        label='Password',
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Invalid username or password")
            if not user.is_active:
                raise ValidationError("This account is inactive")
            cleaned_data['user'] = user
        return cleaned_data

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=100,
        required=True,
        validators=[EmailValidator(message="Please enter a valid email address")],
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Email does not exist")
        return cleaned_data


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        min_length=8,
        required=True,
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        min_length=8,
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError("Passwords do not match")
        return cleaned_data

class PostForm(forms.ModelForm):
    title = forms.CharField(
        label="Title",
        max_length=100,
        required=True,
    )
    content = forms.CharField(
        label="Content",
        required=True,
    )
    category = forms.ModelChoiceField(
        label="Category",
        required=True,
        queryset=Category.objects.all(),
    )
    img_url = forms.ImageField(
        label="Image",
        required=False,
    )

    class Meta:
        model = Post
        fields = ["title", "content", "category", "img_url"]

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        content = cleaned_data.get("content")
        
        # custom validation 
        if title and len(title) < 5:
            raise ValidationError("Title must be at least 5 characters long")
        if content and len(content) < 10:
            raise ValidationError("Content must be at least 10 characters long")
        return cleaned_data

    def save(self, commit=True):
        post = super().save(commit=False)
        if not self.cleaned_data.get("img_url"):
            post.img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/450px-No_image_available.svg.png"
        if commit:
            post.save()
        return post
