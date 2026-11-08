
from django.db.models import Count

from apps.auths.models import User
from apps.blog.models import Post, Comment, Category


def dashboard_callback(request, context):
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(
        status="published"
    ).count()
    draft_posts = Post.objects.filter(
        status="draft"
    ).count()

    categories = Category.objects.annotate(
        posts_count=Count("post")
    ).order_by("-posts_count")

    top_authors = User.objects.annotate(
        posts_count=Count("posts")
    ).order_by("-posts_count", "email")[:5]

    context.update({
        "total_users": User.objects.count(),
        "total_posts": total_posts,
        "total_comments": Comment.objects.count(),
        "total_categories": Category.objects.count(),
        "published_posts": published_posts,
        "draft_posts": draft_posts,
        "published_percent": (
            round(published_posts / total_posts * 100)
            if total_posts else 0
        ),
        "categories_chart": [
            {
                "name": category.name,
                "count": category.posts_count,
            }
            for category in categories
        ],
        "top_authors": top_authors,
    })

    return context
