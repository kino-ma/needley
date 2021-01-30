from django.contrib import admin

# Register your models here.
from .models import User, Article


class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
        (None, {'fields': ['nickname']}),
        (None, {'fields': ['avator']}),
    ]
    list_display = ('name',)
    list_filter = ['name']
    search_fields = ['name', 'nickname']


class ArticleAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title']}),
        (None, {'fields': ['author']}),
        (None, {'fields': ['content']}),
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Article, ArticleAdmin)
