from django.urls import reverse
from django.shortcuts import redirect

class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # List of paths to check
            path_to_redirect = [
                reverse("blog:register"), 
                reverse("blog:login")
            ]

            # Check if the user is trying to access the register or login page
            if request.path in path_to_redirect:
                # Redirect the user to the home page
                return redirect(reverse("blog:index"))

        response = self.get_response(request)
        return response


class RestrictUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        restricted_path = [reverse("blog:dashboard")]

        if not request.user.is_authenticated and request.path in restricted_path:
            return redirect(reverse("blog:login"))
            
        response = self.get_response(request)
        return response