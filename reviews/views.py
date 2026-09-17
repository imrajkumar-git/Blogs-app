from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from accounts.api_permissions import IsOwnerOrAdminOrReadOnly, IsVerifiedUser

from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Public read access to all reviews. A verified, logged-in user may
    create ONE review; submitting again updates their existing review
    instead of creating a duplicate. Only the owner or an admin may
    edit/delete a given review.
    """
    queryset = Review.objects.select_related("user").all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsVerifiedUser, IsOwnerOrAdminOrReadOnly]

    def create(self, request, *args, **kwargs):
        # One review per user: if they already have one, update it instead
        # of erroring out on the OneToOne constraint.
        existing = Review.objects.filter(user=request.user).first()
        serializer = self.get_serializer(existing, data=request.data, partial=bool(existing))
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=200 if existing else 201)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def mine(self, request):
        """Return the current user's own review, if any."""
        review = Review.objects.filter(user=request.user).first()
        if not review:
            return Response(None)
        return Response(self.get_serializer(review).data)
