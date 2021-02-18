from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    # Nickname is display name
    nickname = models.CharField(
        validators=[MinLengthValidator(1)], max_length=20)
    # Avator is a url icon image url
    avatar = models.URLField(
        validators=[MinLengthValidator(1)], max_length=200, null=True)

    def __str__(self):
        return "@%s" % self.username


class Article(models.Model):
    # The author of this article. This field can be referenced by `article.author`
    author = models.ForeignKey(
        User,
        related_name="author",
        on_delete=models.CASCADE
    )
    # The title of this article
    title = models.CharField(
        validators=[MinLengthValidator(1)], max_length=100)
    # Actual content of this article
    content = models.TextField()

    # Date when data were created/updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "\"%s\" by %s" % (self.title, self.author.profile)
