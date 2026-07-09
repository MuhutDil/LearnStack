from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class Learner(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    is_editor = models.BooleanField(default=False, editable=True)

    def __str__(self):
        return self.username
