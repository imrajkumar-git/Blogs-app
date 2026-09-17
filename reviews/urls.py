from django.urls import path

from .views import ReviewViewSet

review_list = ReviewViewSet.as_view({"get": "list", "post": "create"})
review_detail = ReviewViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "put": "update", "delete": "destroy"}
)
review_mine = ReviewViewSet.as_view({"get": "mine"})

urlpatterns = [
    # NOTE: "mine/" must be registered before "<int:pk>/" so it isn't
    # swallowed by the numeric pk pattern.
    path("mine/", review_mine, name="review-mine"),
    path("", review_list, name="review-list"),
    path("<int:pk>/", review_detail, name="review-detail"),
]
