# Set up logging once for the module
import logging
from django.contrib.auth.models import Group
from django.db.models.fields import related
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post 
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from blog.models import Post, AboutUs, Category
from .forms import (
    ContactForm, LoginForm, RegisterForm, ForgotPasswordForm,
    ResetPasswordForm, PostForm
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required

logger = logging.getLogger(__name__)

def index(request):
    # Display paginated list of published blog posts.
    all_posts = Post.objects.filter(is_published=True).select_related('category')
    # Assuming 'all_posts' was something like Post.objects.all()
    all_posts = Post.objects.all().order_by('pk') # Or '-publish_date', 'title' etc.
    
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)
    
    return render(request, "blog/index.html", {
        "blog_title": "Latest Posts",
        "page_obj": paginator.get_page(page_number)
    })

def detail(request, slug):
    # Display detailed view of a single post with related posts.
    post = get_object_or_404(Post, slug=slug)
    
    if request.user and not request.user.has_perm('blog.view_post', post):
        messages.error(request, "You do not have permission to view this post.")
        return redirect('blog:index')

    related_posts = (
        Post.objects.filter(category=post.category)
        .exclude(slug=slug)
        .select_related('category')[:3]
    )
    
    return render(request, "blog/detail.html", {
        "post": post,
        "related_posts": related_posts
    })

def old_url_redirect(request):
    # Handle redirects from old URLs.
    return redirect(reverse("blog:new_page_url"))

def new_url_view(request):
    # Handle new URL endpoint.
    return HttpResponse("This is the new URL.")

def custom_page_not_found_view(request, exception):
    # Custom 404 error handler.
    return render(request, '404.html', status=404)

@require_http_methods(["GET", "POST"])
def contact(request):
    # Handle contact form submission.
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            logger.info(
                "Contact Form Submitted Successfully:\n"
                f"Name: {cleaned_data['name']}\n"
                f"Email: {cleaned_data['email']}\n"
                f"Message: {cleaned_data['message']}"
            )
            messages.success(request, "Thank you for contacting us!")
            return redirect('blog:contact')
        
        logger.error(f"Form validation failed: {form.errors}")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()
    
    return render(request, 'blog/contact.html', {'form': form})

def about(request):
    # Display about page content.
    about_content = AboutUs.objects.first()
    return render(request, 'blog/about.html', {
        'about_content': about_content.content if about_content else "No content available."
    })

@require_http_methods(["GET", "POST"])
def register(request):
    # User registration.
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                
                readers_group, _ = Group.objects.get_or_create(name="Readers")
                user.groups.add(readers_group)
                
                messages.success(request, 'Registration successful! Please log in with your credentials.')
                return redirect('blog:login')
            except Exception as e:
                logger.error(f"Registration failed: {str(e)}")
                messages.error(request, 'Registration failed. Please try again.')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = RegisterForm()
    
    return render(request, 'blog/register.html', {
        'form': form,
        'title': 'Register New Account'
    })

@require_http_methods(["GET", "POST"])
def login(request):
    # User login.
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                auth_login(request, user)
                return redirect(request.GET.get('next', 'blog:dashboard'))
            messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'blog/login.html', {'form': form})

@login_required
def dashboard(request):
    # Display user's dashboard with their posts.
    user_posts = Post.objects.filter(user=request.user)
    paginator = Paginator(user_posts, 5)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'blog/dashbord.html', {
        "blog_title": "My Posts",
        "page_obj": page_obj
    })

@require_http_methods(["GET"])
def logout(request):
    """Handle user logout."""
    auth_logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('blog:index')

def forgot_password(request):
    """Handle forgot password functionality."""
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            User = get_user_model()
            user = User.objects.filter(email=email).first()
            
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                current_site = get_current_site(request)
                
                send_mail(
                    "Password Reset Request",
                    render_to_string('blog/reset_password_email.html', {
                        'domain': current_site.domain,
                        'uid': uid,
                        'token': token,
                    }),
                    "shan_email@pycode.com",
                    [email]
                )
                messages.success(request, "Password reset email sent.")
            else:
                messages.error(request, "No user found with that email address.")
    else:
        form = ForgotPasswordForm()

    return render(request, 'blog/forgot_password.html', {'form': form})

def reset_password(request, uidb64, token):
    """Handle password reset functionality."""
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                User = get_user_model()
                user = User.objects.get(pk=uid)
                
                if user and default_token_generator.check_token(user, token):
                    user.set_password(form.cleaned_data["new_password"])
                    user.save()
                    messages.success(request, "Your password has been reset successfully.")
                    return redirect('blog:login')
                else:
                    messages.error(request, "Invalid password reset link.")
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                messages.error(request, "Invalid password reset link.")
    else:
        form = ResetPasswordForm()

    return render(request, 'blog/reset_password.html', {'form': form})

@login_required
@permission_required('blog.add_post', raise_exception=True)
@require_http_methods(["GET", "POST"])
def new_post(request):
    # New post creation.
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                messages.success(request, "New post created successfully.")
                return redirect('blog:dashboard')
            except Exception as e:
                logger.error(f"Failed to create new post: {str(e)}")
                messages.error(request, "Failed to create post. Please try again.")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = PostForm()

    return render(request, 'blog/new_post.html', {
        'form': form,
        'categories': Category.objects.all(),
        'title': 'Create New Post'
    })

@login_required
@permission_required('blog.change_post', raise_exception=True)
@require_http_methods(["GET", "POST"])
def edit_post(request, post_id):
    # Post editing.
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect('blog:dashboard')
        messages.error(request, "Please correct the errors in the form.")
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/edit_post.html', {
        'categories': Category.objects.all(),
        'post': post,
        'form': form
    })

@login_required
@permission_required('blog.delete_post', raise_exception=True)
@require_http_methods(["GET", "POST"])
def delete_post(request, post_id):
    # Post deletion.
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        try:
            post.delete()
            messages.success(request, "Post deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete post: {str(e)}")
            messages.error(request, "Failed to delete post. Please try again.")
        return redirect('blog:dashboard')

    return render(request, 'blog/delete_post.html', {'post': post})

@login_required
@permission_required('blog.can_publish', raise_exception=True)
def publish_post(request, post_id):
    # Post publication.
    post = get_object_or_404(Post, id=post_id)
    try:
        post.is_published = True
        post.save()
        messages.success(request, "Post published successfully.")
    except Exception as e:
        logger.error(f"Failed to publish post: {str(e)}")
        messages.error(request, "Failed to publish post. Please try again.")
    return redirect('blog:dashboard')