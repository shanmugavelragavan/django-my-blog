from django.shortcuts import render

def custom_page_not_found_view(request, exception):
    return render(request, "404.html, status=404")