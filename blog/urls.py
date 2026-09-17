from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, CommentDeleteView

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")

urlpatterns = [
    path("comments/<int:pk>/", CommentDeleteView.as_view(), name="comment-delete"),
    path("", include(router.urls)),
]
