from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import RegistrationForm
from django.contrib.auth import login as auth_login
import logging
from django.contrib.auth import login as django_login


def home(request):
    return render(request, 'frontend_littleheart/index.html')
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('rememberMe')  

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Set session expiry based on "Remember me"
            if remember_me:
                request.session.set_expiry(604800)  # 7 days in seconds (7 * 24 * 60 * 60)
            else:
                request.session.set_expiry(0)  # Session expires on browser close
            messages.success(request, "Login successful!")
            return redirect('home')  # Redirect to home page
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'frontend_littleheart/login.html')

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']
            password = form.cleaned_data['password']

            if not phone.startswith('+977'):
                messages.error(request, "Phone number must start with +977 for Nepal.")
                return render(request, 'frontend_littleheart/register.html', {'form': form})

            # Create new user
            user = User.objects.create_user(username=username, email=email, password=password)
            try:
                # Create user profile
                profile = UserProfile.objects.create(user=user, phone=phone, address=address)
                # Authenticate the user
                authenticated_user = authenticate(request, username=username, password=password)
                if authenticated_user is not None:
                    django_login(request, authenticated_user)  
                    messages.success(request, "Registration successful! You are now logged in.")
                    return redirect('login')
                else:
                    messages.error(request, "Authentication failed after registration.")
            except Exception as e:
                # Delete the user if profile creation fails
                user.delete()
                logger.error(f"Registration error for user {username}: {str(e)}")
                if "Duplicate entry" in str(e):
                    messages.error(request, "The phone number is already registered. Please use a different number.")
                else:
                    messages.error(request, f"An error occurred during registration: {str(e)}. Check server logs for details.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'frontend_littleheart/register.html', {'form': form})

def about(request):
    return render(request, 'frontend_littleheart/about.html')
def blog(request):
    return render(request, 'frontend_littleheart/blog.html')
def contact(request):
    return render(request, 'frontend_littleheart/contact.html')

def grooming(request):
    return render(request, 'frontend_littleheart/grooming.html')

def regular_bathing(request):
    return render(request, 'frontend_littleheart/regular_bath.html')

def dog(request):
    return render(request, 'frontend_littleheart/dog.html')

def cat(request):
    return render(request, 'frontend_littleheart/cat.html')