from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    tags = models.JSONField(default=list)
    email = models.EmailField(default='', unique=True)
    password = models.CharField(max_length=100)
    username = models.CharField(max_length=255,unique=True, default='')
    
    USERNAME_FIELD='username'
    REQUIRED_FIELDS=[]
class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    bio = models.TextField()
    displayName = models.CharField(max_length=255)
    tags = models.JSONField(default=list)
    followers = models.PositiveIntegerField()