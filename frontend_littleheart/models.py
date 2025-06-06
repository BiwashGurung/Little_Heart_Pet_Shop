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