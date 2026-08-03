from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Category, Comment, Post, Tag

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with sample categories, tags, posts and comments."

    def handle(self, *args, **options):
        author, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True},
        )
        if created:
            author.set_password("admin12345")
            author.save()
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' / 'admin12345'"))

        categories = {}
        for name in ["Technology", "Travel", "Lifestyle", "Programming"]:
            categories[name], _ = Category.objects.get_or_create(name=name)

        tags = {}
        for name in ["Django", "Next.js", "React", "Python", "Tutorial", "Opinion"]:
            tags[name], _ = Tag.objects.get_or_create(name=name)

        sample_posts = [
            {
                "title": "Building a Blog API with Django REST Framework",
                "category": "Programming",
                "tags": ["Django", "Python", "Tutorial"],
                "excerpt": "A practical walkthrough of building a clean, production-ready blog API.",
                "content": (
                    "Django REST Framework gives you serializers, viewsets, and routers "
                    "that make building a blog API straightforward. In this post we walk "
                    "through models, serializers, permissions, and pagination step by step, "
                    "and end with a fully working set of endpoints ready for a frontend to "
                    "consume." * 3
                ),
                "is_featured": True,
            },
            {
                "title": "Why Next.js is a Great Fit for Content Sites",
                "category": "Technology",
                "tags": ["Next.js", "React", "Opinion"],
                "excerpt": "Server components, fast routing, and great SEO defaults.",
                "content": (
                    "Next.js combines server-side rendering, static generation, and a "
                    "modern React developer experience. For content-heavy sites like blogs, "
                    "that means fast first loads, easy SEO, and simple data fetching "
                    "patterns using the App Router." * 3
                ),
                "is_featured": True,
            },
            {
                "title": "Five Lessons from a Year of Remote Work",
                "category": "Lifestyle",
                "tags": ["Opinion"],
                "excerpt": "What actually changed after twelve months away from the office.",
                "content": (
                    "Remote work rewards clear communication and honest boundaries. "
                    "Here are five lessons that made the biggest difference to how our "
                    "team collaborates, plans, and stays connected." * 3
                ),
                "is_featured": False,
            },
        ]

        for data in sample_posts:
            post, _ = Post.objects.get_or_create(
                title=data["title"],
                defaults={
                    "author": author,
                    "category": categories[data["category"]],
                    "excerpt": data["excerpt"],
                    "content": data["content"],
                    "status": Post.Status.PUBLISHED,
                    "is_featured": data["is_featured"],
                    "published_at": timezone.now(),
                },
            )
            post.tags.set([tags[t] for t in data["tags"]])

            Comment.objects.get_or_create(
                post=post,
                name="Jamie Rivera",
                email="jamie@example.com",
                content="Really enjoyed this — clear and to the point!",
                defaults={"is_approved": True},
            )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
