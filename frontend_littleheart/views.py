from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import RegistrationForm
from django.contrib.auth import login as auth_login
import logging
from django.contrib.auth import login as django_login
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from .models import Blog, Contact
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import OTP
import random
from django.utils import timezone



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

            # Check if OTP is being verified (from modal submission)
            if 'otp' in request.POST and request.POST.get('action') == 'verify_otp':
                otp_input = request.POST.get('otp')
                try:
                    # Get the most recent unverified OTP
                    otp = OTP.objects.filter(email=email, is_verified=False).order_by('-created_at').first()
                    if otp and otp.otp_code == otp_input and timezone.now() < otp.expires_at:
                        otp.is_verified = True
                        otp.save()
                        # Create user and profile
                        user = User.objects.create_user(username=username, email=email, password=password)
                        profile = UserProfile.objects.create(user=user, phone=phone, address=address)
                        authenticated_user = authenticate(request, username=username, password=password)
                        if authenticated_user is not None:
                            django_login(request, authenticated_user)
                            messages.success(request, "Registration successful! You are now logged in.")
                            otp.delete()  # Clean up OTP
                            return redirect('login')
                        else:
                            messages.error(request, "Authentication failed after registration.")
                    else:
                        messages.error(request, "Invalid or expired OTP. Please try again.")
                except OTP.DoesNotExist:
                    messages.error(request, "No OTP found for this email. Please request a new one.")
                return render(request, 'frontend_littleheart/register.html', {'form': form, 'show_modal': True})
            else:
                # Check for existing unverified OTPs and clean up
                OTP.objects.filter(email=email, is_verified=False).exclude(expires_at__lt=timezone.now()).delete()
                # Generate and send new OTP
                otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                otp = OTP.objects.create(
                    email=email,
                    otp_code=otp_code,
                    expires_at=timezone.now() + timezone.timedelta(minutes=10)
                )
                try:
                    send_mail(
                        subject="Your OTP for Registration",
                        message=f"Your OTP code is {otp_code}. It is valid for 10 minutes. Do not share it with anyone.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                    messages.success(request, f"OTP has been sent to {email}. Please verify it in the popup.")
                except Exception as e:
                    logger.error(f"OTP email sending failed for {email}: {str(e)}")
                    messages.error(request, f"Failed to send OTP. Please try again later.")
                    otp.delete()  # Clean up if email fails
                return render(request, 'frontend_littleheart/register.html', {'form': form, 'show_modal': True})
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'frontend_littleheart/register.html', {'form': form})

def about(request):
    return render(request, 'frontend_littleheart/about.html')



def blog_list(request):
    blogs = Blog.objects.all()
    paginator = Paginator(blogs, 4)  # Show 4 blogs per page to match your layout
    page = request.GET.get('page')
    try:
        blogs_page = paginator.page(page)
    except PageNotAnInteger:
        blogs_page = paginator.page(1)
    except EmptyPage:
        blogs_page = paginator.page(paginator.num_pages)
    return render(request, 'frontend_littleheart/blog.html', {'blogs': blogs_page})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    # Get other blogs, excluding the current one, limited to 4
    other_blogs = Blog.objects.exclude(id=blog.id).order_by('-created_at')[:4]
    return render(request, 'frontend_littleheart/blog_detail.html', {'blog': blog, 'other_blogs': other_blogs})



def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            # Send email
            try:
                send_mail(
                    subject=f"New Contact Form Submission: {contact.subject}",
                    message=f"Name: {contact.name}\nEmail: {contact.email}\nPhone: {contact.phone or 'Not provided'}\nMessage: {contact.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],  # Send to admin email
                    fail_silently=False,
                )
                messages.success(request, "Thank you! Your message has been sent successfully.")
            except Exception as e:
                logger.error(f"Email sending failed for contact {contact.id}: {str(e)}")
                messages.error(request, "Message saved, but email sending failed. Please contact support.")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()
    return render(request, 'frontend_littleheart/contact.html', {'form': form})

def grooming(request):
    return render(request, 'frontend_littleheart/grooming.html')

def regular_bathing(request):
    return render(request, 'frontend_littleheart/regular_bath.html')

def dog(request):
    return render(request, 'frontend_littleheart/dog.html')

def cat(request):
    return render(request, 'frontend_littleheart/cat.html')