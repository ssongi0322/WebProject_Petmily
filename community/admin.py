from django.contrib import admin
from .models import Post,Answer,Comment,Image


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "writer", "created_at")


admin.site.register(Post, PostAdmin)
admin.site.register(Answer)
admin.site.register(Comment)
admin.site.register(Image)