from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import json
from datetime import timedelta
from .models import Booking
from django.utils import timezone
import random
import logging
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .forms import RegistrationForm, ContactForm
from .models import UserProfile, Contact, Blog, OTP
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import login as django_login
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


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



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from .models import Booking
import json

@login_required
def regular_bathing(request):
    return render(request, 'frontend_littleheart/regular_bath.html', {})

@csrf_exempt
@login_required
def get_time_slots(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'success': False, 'message': 'Date parameter is required'}, status=400)

    try:
        date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        today = timezone.now().date()
        max_date = today + timedelta(days=30)

        if not (today <= date <= max_date):
            return JsonResponse({'success': False, 'message': 'Please select a date within the next 30 days.'}, status=400)

        # Generate time slots from 9:00 AM to 4:00 PM in 15-minute increments
        time_slots = []
        for hour in range(9, 17):  # 9 AM to 4 PM
            for minute in [0, 15, 30, 45]:
                if hour == 16 and minute > 0:  # Exclude after 4:00 PM
                    continue
                time_str = f"{hour:02d}:{minute:02d}"
                if hour == 0:
                    display_time = f"12:{minute:02d} AM"
                elif hour < 12:
                    display_time = f"{hour}:{minute:02d} AM"
                elif hour == 12:
                    display_time = f"12:{minute:02d} PM"
                else:
                    display_time = f"{hour - 12}:{minute:02d} PM"
                time_slots.append(display_time)

        # Exclude booked slots
        booked_times = Booking.objects.filter(date_time__date=date).values_list('date_time__time', flat=True)
        available_slots = [slot for slot in time_slots if slot not in booked_times]

        return JsonResponse({'success': True, 'time_slots': available_slots})
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid date format'}, status=400)

@csrf_exempt
@login_required
def book_appointment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pets = data.get('pets', [])
            service_type = data.get('service_type')
            add_ons = data.get('add_ons', [])
            date_time_str = data.get('date_time')
            total_price = calculate_total_price(service_type, add_ons)

            # Convert to datetime
            date_time = timezone.datetime.strptime(date_time_str, '%Y-%m-%d %I:%M %p')

            # Check for existing booking
            existing_booking = Booking.objects.filter(date_time=date_time).exists()
            if existing_booking:
                return JsonResponse({'success': False, 'message': 'This date and time is already booked.'})

            # Validate date range
            today = timezone.now().date()
            max_date = today + timedelta(days=30)
            if not (today <= date_time.date() <= max_date):
                return JsonResponse({'success': False, 'message': 'Please select a date within the next 30 days.'})

            booking = Booking(
                user=request.user,
                full_name=data.get('full_name'),
                contact_no=data.get('contact_no'),
                email=data.get('email'),
                pets=pets,
                service_type=service_type,
                add_ons=add_ons,
                date_time=date_time,
                total_price=total_price
            )
            booking.save()

            send_booking_email(booking, request.user.email)
            return JsonResponse({'success': True, 'message': 'Booking saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    if request.user.is_staff:
        all_bookings = Booking.objects.all().order_by('-created_at')
        return render(request, 'frontend_littleheart/my_bookings.html', {'bookings': all_bookings, 'is_staff': True})
    return render(request, 'frontend_littleheart/my_bookings.html', {'bookings': bookings})

@csrf_exempt
@login_required
def update_booking_status(request):
    if request.method == 'POST' and request.user.is_staff:
        booking_id = request.POST.get('booking_id')
        status = request.POST.get('status')
        try:
            booking = Booking.objects.get(id=booking_id)
            booking.status = status
            booking.save()
            send_status_update_email(booking, booking.email)
            return JsonResponse({'success': True, 'message': 'Status updated successfully'})
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Booking not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request or insufficient permissions'})

def calculate_total_price(service_type, add_ons):
    base_prices = {'washDry': 1800, 'washTidy': 2000, 'fullGroom': 2500, 'puppy': 2000}
    add_on_prices = {'deshedding': 500, 'specialShampoo': 300, 'nailClip': 200, 'analGland': 400, 'teethBrushing': 300}
    total = base_prices.get(service_type, 0)
    for add_on in add_ons:
        total += add_on_prices.get(add_on, 0)
    return total

def send_booking_email(booking, recipient_email):
    subject = 'Your Pet Grooming Booking Confirmation'
    message = f"""
    Dear {booking.full_name},

    Your booking has been successfully created with the following details:
    - Date & Time: {booking.date_time}
    - Service Type: {booking.service_type}
    - Total Price: Rs. {booking.total_price}
    - Status: {booking.status}
    - Pets: {booking.pets}

    Thank you for choosing us!
    Little Heart Pet Shop
    """
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [recipient_email],
        fail_silently=False,
    )

def send_status_update_email(booking, recipient_email):
    subject = 'Your Pet Grooming Booking Status Update'
    message = f"""
    Dear {booking.full_name},

    The status of your booking has been updated to: {booking.status}

    Booking Details:
    - Date & Time: {booking.date_time}
    - Service Type: {booking.service_type}
    - Total Price: Rs. {booking.total_price}
    - Pets: {booking.pets}

    Thank you!
    Little Heart Pet Shop
    """
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [recipient_email],
        fail_silently=False,
    )