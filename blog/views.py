from django.db.models import Q
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from accounts.api_permissions import IsOwnerOrAdminOrReadOnly, IsVerifiedUser

from .models import Post, Comment, Like
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostWriteSerializer,
    CommentSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """
    Public read access to published posts. Creating a post requires a
    verified, logged-in user; editing/deleting requires being the author
    or an admin.
    """
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly, IsVerifiedUser, IsOwnerOrAdminOrReadOnly]
    # MultiPart/Form parsers let authors upload a cover image straight from
    # their device; JSON still works for clients that only send text.
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostWriteSerializer

    def get_queryset(self):
        qs = Post.objects.select_related("author").prefetch_related("likes", "comments__user")
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return qs
            # Everyone sees published posts; authors additionally see their own drafts.
            return qs.filter(Q(is_published=True) | Q(author=user))
        return qs.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        # Remove the uploaded file along with the post.
        if instance.cover_image:
            instance.cover_image.delete(save=False)
        instance.delete()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        """Toggle a like on this post for the current user."""
        post = self.get_object()
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return Response({"liked": liked, "likes_count": post.likes.count()})

    @action(
        detail=True,
        methods=["get", "post"],
        permission_classes=[IsAuthenticatedOrReadOnly, IsVerifiedUser],
        url_path="comments",
    )
    def comments(self, request, slug=None):
        """GET: list comments on this post. POST: add a comment (verified users only)."""
        post = self.get_object()
        if request.method == "GET":
            serializer = CommentSerializer(
                post.comments.select_related("user"), many=True
            )
            return Response(serializer.data)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDeleteView(generics.DestroyAPIView):
    """Delete a single comment — only its author or an admin may do this."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrReadOnly]
