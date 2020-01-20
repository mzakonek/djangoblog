from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True, related_name='post_likes')
    favorites = models.ManyToManyField(User, through="Favoritepost", related_name='post_favorites')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

    def get_like_url(self):
        return reverse("post-like_toogle", kwargs={'pk': self.pk})

    def get_api_like_url(self):
        return reverse("post-like_api_toogle", kwargs={'pk': self.pk})

    def get_api_favorite_url(self):
        return reverse("post-favorite_api_toogle", kwargs={'pk': self.pk})


class Favoritepost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorite_posts')
    index = models.IntegerField(default=-1, unique=True)

    def save(self, *args, **kwargs):
        self.index = self.user.post_favourites.count() + 1
        super(Favoritepost, self).save(*args, **kwargs)

