from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("post/<str:slug>/", views.detail, name="detail"), 
    path("new-page/", views.new_url_view, name="new_page"),
    path("redirect/", views.old_url_redirect, name="redirect"),
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name='blog/login.html'), name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/<uidb64>/<token>/", views.reset_password, name="reset_password"),
    path("new_post/", views.new_post, name="new_post"),
    path("edit_post/<int:post_id>/", views.edit_post, name="edit_post"),
    path("delete_post/<int:post_id>/", views.delete_post, name="delete_post"),
    path("publish_post/<int:post_id>/", views.publish_post, name="publish_post")
]
