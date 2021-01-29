from django.db import models
from django.utils import timezone


class User(models.Model):
    # @someones_name
    name = models.CharField(min_length=1, max_length=30)
    # Nickname is display name
    nickname = models.CharField(min_length=1, max_length=20)
    # Avator is a url icon image url
    avator = models.URLField(min_length=1, max_length=200)

    # Date when data were created/updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "@%s" % self.name


class Article(models.Model):
    # The author of this article. This field can be referenced by `article.author`
    author = models.ForeignKey(
        User,
        related_name="author",
        on_delete=models.CASCADE
    )
    # The title of this article
    title = models.CharField(min_length=1, max_length=100)
    # Actual content of this article
    content = models.TextField()

    # Date when data were created/updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "\"%s\" by @%s" % (self.title, self.author)

