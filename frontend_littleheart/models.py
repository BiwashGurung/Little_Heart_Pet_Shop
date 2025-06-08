from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()

    class Meta:
        db_table = 'little_heart_users'  # Set the table name to little_heart_users

    def __str__(self):
        return f"{self.user.username}'s Profile"
    


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)  # Optional phone field
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'little_heart_contacts'

    def __str__(self):
        return f"{self.name} - {self.subject}"