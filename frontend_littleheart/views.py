from django.shortcuts import render


def home(request):
    return render(request, 'frontend_littleheart/index.html')