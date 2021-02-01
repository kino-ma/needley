from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User





class Profile(models.Model):
    # User authentication model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Nickname is display name
    nickname = models.CharField(
        validators=[MinLengthValidator(1)], max_length=20)
    # Avator is a url icon image url
    avator = models.URLField(
        validators=[MinLengthValidator(1)], max_length=200, null=True)

    def __str__(self):
        return "@%s" % self.user.username

    @classmethod
    def lookup_name(cls, name):
        try:
            return User.objects.get(name=name)
        except User.DoesNotExist:
            return None


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
