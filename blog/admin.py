from django.contrib import admin
from .models import Post, Like, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "is_published", "has_cover", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "author__email", "author__username")
    prepopulated_fields = {"slug": ("title",)}

    @admin.display(boolean=True, description="Cover")
    def has_cover(self, obj):
        return bool(obj.cover_image or obj.cover_image_url)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
    search_fields = ("post__title", "user__email")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
