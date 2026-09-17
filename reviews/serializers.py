from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Review

User = get_user_model()


class ReviewerMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewerMiniSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Review cannot be empty.")
        return value
