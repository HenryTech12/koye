from django.db import models
from userapp.models import User
# Create your models here.
class Artwork(models.Model):
    creator=models.ForeignKey(User,on_delete=models.CASCADE,related_name="uploads")
    name = models.CharField(max_length=100, default='')
    location = models.CharField(max_length=200, default='')
    desc = models.TextField(blank=True,null=True)
    tags = models.JSONField(default=list)
    fileUrl = models.TextField(blank=True, null=True)
    likes = models.IntegerField(default=0)
    saves = models.IntegerField(default=0)
    data = models.JSONField(default=dict)
    
