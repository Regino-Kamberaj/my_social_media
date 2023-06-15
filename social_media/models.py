import uuid
from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()  # lo inizializza


class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profile_img = models.ImageField(upload_to='profile_images',default='blank-profile-picture.png')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images', default='blank-profile-picture.png')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    number_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user

class LikePost(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    liked = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class FollowersCount(models.Model):
    follower = models.CharField(max_length=100) # qui ci va il nome di chi ha inizato a seguirti
    user = models.CharField(max_length=100)

    def __str__(self):
        return f"User: {self.user} and follower: {self.follower}"

class CommentPost(models.Model): # Da implementare la funzionalità per aggiungere un commento...
    username = models.CharField(max_length=100)
    post_id = models.IntegerField(unique=True)
    text = models.TextField()

    def __str__(self):
        return self.username
