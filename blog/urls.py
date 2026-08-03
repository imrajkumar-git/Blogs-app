from django.urls import include, path
from rest_framework import views
from rest_framework.routers import DefaultRouter
from .views import home
from .views import CategoryViewSet, CommentViewSet, PostViewSet, TagViewSet

router = DefaultRouter()

router.register("posts", PostViewSet, basename="post")
router.register("categories", CategoryViewSet, basename="category")
router.register("tags", TagViewSet, basename="tag")
router.register("comments", CommentViewSet, basename="comment")

urlpatterns = [
    path('', home, name='home'),
    path("api/", include(router.urls)),]
