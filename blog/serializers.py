from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Post, Comment, Like

User = get_user_model()


class AuthorMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class CommentSerializer(serializers.ModelSerializer):
    user = AuthorMiniSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "user", "content", "created_at"]
        read_only_fields = ["id", "post", "user", "created_at"]

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Comment cannot be empty.")
        return value


class PostListSerializer(serializers.ModelSerializer):
    author = AuthorMiniSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()
    # `cover` is the one field the frontend reads. It resolves an uploaded
    # file first and falls back to the external URL, always absolute.
    cover = serializers.SerializerMethodField()
    cover_image = serializers.ImageField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "excerpt",
            "cover", "cover_image", "cover_image_url", "author",
            "is_published", "created_at", "updated_at",
            "likes_count", "comments_count", "liked_by_me",
        ]

    def get_cover(self, obj):
        request = self.context.get("request")
        if obj.cover_image:
            url = obj.cover_image.url
            return request.build_absolute_uri(url) if request else url
        return obj.cover_image_url or ""

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_liked_by_me(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()


class PostDetailSerializer(PostListSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ["content", "comments"]


class PostWriteSerializer(serializers.ModelSerializer):
    """
    Accepts both JSON and multipart/form-data. When the author picks a file
    from their device the request arrives as multipart with `cover_image`;
    `remove_cover_image=true` clears an existing upload.
    """

    cover_image = serializers.ImageField(required=False, allow_null=True)
    remove_cover_image = serializers.BooleanField(
        required=False, write_only=True, default=False
    )
    cover = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "slug", "title", "excerpt", "content",
            "cover", "cover_image", "cover_image_url",
            "remove_cover_image", "is_published",
        ]
        read_only_fields = ["id", "slug"]

    def get_cover(self, obj):
        request = self.context.get("request")
        if obj.cover_image:
            url = obj.cover_image.url
            return request.build_absolute_uri(url) if request else url
        return obj.cover_image_url or ""

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_cover_image(self, value):
        if value in (None, ""):
            return value
        max_bytes = getattr(settings, "BLOG_COVER_MAX_BYTES", 5 * 1024 * 1024)
        if value.size > max_bytes:
            raise serializers.ValidationError(
                f"Cover image must be {max_bytes // (1024 * 1024)}MB or smaller."
            )
        return value

    def _apply_removal(self, instance, remove):
        if remove and instance.cover_image:
            instance.cover_image.delete(save=False)
            instance.cover_image = None

    def create(self, validated_data):
        validated_data.pop("remove_cover_image", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remove = validated_data.pop("remove_cover_image", False)
        new_file = validated_data.get("cover_image", None)

        # Replacing or clearing an upload deletes the old file so media/
        # doesn't fill up with orphans.
        if (new_file or remove) and instance.cover_image:
            instance.cover_image.delete(save=False)
            instance.cover_image = None

        instance = super().update(instance, validated_data)
        if remove and not new_file:
            instance.cover_image = None
            instance.save(update_fields=["cover_image"])
        return instance
