from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils import timezone

from .models import Category, Comment, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "post_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = "Posts"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("name", "email", "content", "is_approved", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "thumbnail",
        "author",
        "category",
        "status_badge",
        "is_featured",
        "views_count",
        "published_at",
    )
    list_display_links = ("title",)
    list_filter = ("status", "is_featured", "category", "tags", "created_at")
    search_fields = ("title", "excerpt", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author", "category")
    filter_horizontal = ("tags",)
    date_hierarchy = "created_at"
    list_editable = ("is_featured",)
    readonly_fields = ("views_count", "created_at", "updated_at", "image_preview")
    inlines = [CommentInline]
    actions = ["publish_posts", "unpublish_posts", "mark_featured", "unmark_featured"]
    save_on_top = True

    fieldsets = (
        ("Content", {
            "fields": ("title", "slug", "author", "category", "tags", "excerpt", "content"),
        }),
        ("Media", {
            "fields": ("featured_image", "image_preview"),
        }),
        ("Publishing", {
            "fields": ("status", "is_featured", "published_at"),
        }),
        ("Stats", {
            "fields": ("views_count", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    class Media:
        css = {"all": ("admin/css/custom_admin.css",)}

    def thumbnail(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="height:40px;width:60px;object-fit:cover;'
                'border-radius:6px;" />',
                obj.featured_image.url,
            )
        return "—"

    thumbnail.short_description = "Image"

    def image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-height:220px;border-radius:10px;" />',
                obj.featured_image.url,
            )
        return "No image uploaded yet."

    image_preview.short_description = "Preview"

    def status_badge(self, obj):
        colors = {"draft": "#f0ad4e", "published": "#28a745"}
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;'
            'text-transform:uppercase;letter-spacing:.03em;">{}</span>',
            colors.get(obj.status, "#999"),
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    @admin.action(description="Publish selected posts")
    def publish_posts(self, request, queryset):
        updated = 0
        for post in queryset:
            post.status = Post.Status.PUBLISHED
            if not post.published_at:
                post.published_at = timezone.now()
            post.save()
            updated += 1
        self.message_user(request, f"{updated} post(s) published.", messages.SUCCESS)

    @admin.action(description="Move selected posts back to draft")
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(status=Post.Status.DRAFT)
        self.message_user(request, f"{updated} post(s) moved to draft.", messages.SUCCESS)

    @admin.action(description="Mark selected posts as featured")
    def mark_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} post(s) marked featured.", messages.SUCCESS)

    @admin.action(description="Remove featured flag")
    def unmark_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} post(s) un-featured.", messages.SUCCESS)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "post", "short_content", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "email", "content", "post__title")
    list_editable = ("is_approved",)
    actions = ["approve_comments", "reject_comments"]

    def short_content(self, obj):
        return (obj.content[:60] + "…") if len(obj.content) > 60 else obj.content

    short_content.short_description = "Comment"

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} comment(s) approved.", messages.SUCCESS)

    @admin.action(description="Reject selected comments")
    def reject_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} comment(s) rejected.", messages.SUCCESS)


admin.site.site_header = "Blog Studio Admin"
admin.site.site_title = "Blog Studio"
admin.site.index_title = "Dashboard"
