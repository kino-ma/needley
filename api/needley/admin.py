from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as BaseUser

# Register your models here.
from .models import Article

User = get_user_model()
UserAdmin.list_display = ('username', 'email', 'nickname', 'avatar', 'is_staff')


class ArticleAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title']}),
        (None, {'fields': ['author']}),
        (None, {'fields': ['content']}),
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Article, ArticleAdmin)
