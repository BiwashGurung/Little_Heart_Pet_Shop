from django.contrib import admin
from django.urls import path, include
from frontend_littleheart import views  
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    # Add other URL patterns as needed (e.g., for products, about, etc.)
    # path('products/', views.products, name='products'),
    # path('about/', views.about, name='about'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])