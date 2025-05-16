from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    admin = models.BooleanField(default=False)