from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.
from .models import Profile, Article


class ProfileInline(admin.StackedInline):
    model = Profile
    fieldsets = [
        (None, {'fields': ['nickname']}),
        (None, {'fields': ['avator']}),
    ]
    search_fields = ['nickname']


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )


class ArticleAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title']}),
        (None, {'fields': ['author']}),
        (None, {'fields': ['content']}),
    ]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Article, ArticleAdmin)
