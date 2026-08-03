from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, Comment, Post, Tag

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "name"]

    def get_name(self, obj):
        full_name = obj.get_full_name()
        return full_name or obj.username


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "post_count"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "post", "name", "email", "content", "created_at", "is_approved"]
        read_only_fields = ["id", "created_at", "is_approved"]
        extra_kwargs = {"email": {"write_only": True}}


class PostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer used for listing pages."""

    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reading_time_minutes = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "author",
            "category",
            "tags",
            "excerpt",
            "featured_image",
            "status",
            "is_featured",
            "views_count",
            "reading_time_minutes",
            "published_at",
            "created_at",
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """Full serializer used for the single-post page; includes comments."""

    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    reading_time_minutes = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "author",
            "category",
            "tags",
            "excerpt",
            "content",
            "featured_image",
            "status",
            "is_featured",
            "views_count",
            "reading_time_minutes",
            "comments",
            "published_at",
            "created_at",
            "updated_at",
        ]

    def get_comments(self, obj):
        approved = obj.comments.filter(is_approved=True)
        return CommentSerializer(approved, many=True).data


class PostWriteSerializer(serializers.ModelSerializer):
    """Used by authenticated clients (e.g. admin tooling) to create/update posts."""

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "tags",
            "excerpt",
            "content",
            "featured_image",
            "status",
            "is_featured",
        ]
        read_only_fields = ["id", "slug"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
