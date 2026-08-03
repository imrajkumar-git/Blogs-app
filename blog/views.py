import django_filters
from django.db.models import Count, F
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Comment, Post, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostWriteSerializer,
    TagSerializer,
)


class PostFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__slug")
    tag = django_filters.CharFilter(field_name="tags__slug")

    class Meta:
        model = Post
        fields = ["category", "tag", "is_featured", "status"]


class PostViewSet(viewsets.ModelViewSet):
    """
    Public: list & retrieve published posts.
    Authenticated authors: create/update/delete their own posts.
    """

    queryset = Post.objects.select_related("author", "category").prefetch_related("tags")
    lookup_field = "slug"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filterset_class = PostFilter
    search_fields = ["title", "excerpt", "content"]
    ordering_fields = ["published_at", "created_at", "views_count", "title"]
    ordering = ["-published_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(status=Post.Status.PUBLISHED)

    def get_serializer_class(self):
        if self.action in ("list",):
            return PostListSerializer
        if self.action in ("create", "update", "partial_update"):
            return PostWriteSerializer
        return PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Post.objects.filter(pk=instance.pk).update(views_count=F("views_count") + 1)
        instance.refresh_from_db(fields=["views_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True)[:5]
        serializer = PostListSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.annotate(post_count=Count("posts")).order_by("name")
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]


class CommentViewSet(viewsets.ModelViewSet):
    """Anyone can submit a comment; it stays hidden until approved in the admin."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ["get", "post", "head", "options"]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset().filter(is_approved=True)
        post_slug = self.request.query_params.get("post_slug")
        if post_slug:
            qs = qs.filter(post__slug=post_slug)
        return qs
