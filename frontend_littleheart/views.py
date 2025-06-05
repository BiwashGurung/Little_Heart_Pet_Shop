from django.shortcuts import render


def home(request):
    return render(request, 'frontend_littleheart/index.html')

def login(request):
    return render(request, 'frontend_littleheart/login.html')
def register(request):
    return render(request, 'frontend_littleheart/register.html')
def about(request):
    return render(request, 'frontend_littleheart/about.html')
def blog(request):
    return render(request, 'frontend_littleheart/blog.html')
def contact(request):
    return render(request, 'frontend_littleheart/contact.html')