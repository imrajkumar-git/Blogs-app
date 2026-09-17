import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


def blog_cover_path(instance, filename):
    """Store covers under media/blog_covers/<author id>/<filename>."""
    base, ext = os.path.splitext(filename)
    safe = slugify(base)[:60] or "cover"
    return f"blog_covers/{instance.author_id or 'unassigned'}/{safe}{ext.lower()}"


def validate_cover_image(file):
    """Keep uploads to a sane size and to real image formats."""
    max_bytes = getattr(settings, "BLOG_COVER_MAX_BYTES", 5 * 1024 * 1024)
    if file.size > max_bytes:
        raise ValidationError(
            f"Cover image must be {max_bytes // (1024 * 1024)}MB or smaller."
        )
    ext = os.path.splitext(file.name)[1].lower()
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
    if ext not in allowed:
        raise ValidationError(
            "Unsupported image type. Use JPG, PNG, WEBP, GIF or AVIF."
        )


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    # Two ways to give a post a cover:
    #   cover_image      — a file uploaded from the author's device (preferred)
    #   cover_image_url  — an external URL, kept for existing posts
    cover_image = models.ImageField(
        upload_to=blog_cover_path,
        blank=True,
        null=True,
        validators=[validate_cover_image],
    )
    cover_image_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "post"
            slug = base
            i = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def cover_source(self):
        """The image the site should actually render, upload taking priority."""
        if self.cover_image:
            return self.cover_image.url
        return self.cover_image_url or ""

    def __str__(self):
        return self.title


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_post_like")
        ]

    def __str__(self):
        return f"{self.user} likes {self.post}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"
