from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id_display', 'username_display', 'email_display', 'phone', 'address')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('user',)

    def user_id_display(self, obj):
        return obj.user.id
    user_id_display.short_description = 'User ID'

    def username_display(self, obj):
        return obj.user.username
    username_display.short_description = 'Username'

    def email_display(self, obj):
        return obj.user.email
    email_display.short_description = 'Email'


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')  # Optimize query with select_related

admin.site.register(UserProfile, UserProfileAdmin)