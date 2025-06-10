from django.contrib import admin
from django.urls import path, include
from frontend_littleheart import views  
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact, name='contact'),
    path('grooming/', views.grooming, name='grooming'),
    path('regular_bathing/', views.regular_bathing, name='regular_bathing'),
    path('dog/', views.dog, name='dog'),
    path('cat/', views.cat, name='cat'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('update-booking-status/', views.update_booking_status, name='update_booking_status'),



] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)