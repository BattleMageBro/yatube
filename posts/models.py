from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()


class Post(models.Model):
    text = models.TextField(max_length=200)
    pub_date = models.DateTimeField("date published", auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True, related_name="group_posts")
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    
    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_comments")
    text = models.TextField(max_length=200)
    created = models.DateTimeField("date published", auto_now_add=True, db_index=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")