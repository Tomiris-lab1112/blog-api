from django.db.models import F, Q, QuerySet, Count, Avg, Min, Max, Case, When, CharField

from apps.blog.models import Category, Post 
from apps.auths.models import User
from datetime import date, timedelta
from django.utils import timezone
from apps.blog.models import Comment
from typing import Any 
from django.db.models.functions import Coalesce
from django.db.models.functions import Concat, TruncMonth
from django.db.models import Value
from apps.blog.models import Category, Post, Comment, Tag
from django.utils.text import slugify
from django.db.models import Prefetch
from django.db.models import OuterRef, Subquery
from django.db.models import Exists

def categories_by_name() -> QuerySet[Category]:
    """Return all categories sorted alphabetically"""
    return Category.objects.order_by("name")

def published_posts() -> QuerySet[Post]:
    """Return published posts, newest first"""
    return Post.objects.filter(
        status=Post.Status.PUBLISHED
    ).order_by("-created_at")

def newest_published_posts() -> QuerySet[Post]:
    """Return 5 newest published posts"""
    return published_posts()[:5]

def post_by_slug(slug: str) -> Post | None:
    """Find a post by its slug"""
    return Post.objects.filter(slug=slug).first()

def active_users_count() -> int:
    """Count active users who are not staff"""
    return User.objects.filter(
        is_active=True,
        is_staff=False,
    ).count()

def has_drafts() -> bool:
    """Check whether draft posts exist"""
    return Post.objects.filter(
        status=Post.Status.DRAFT
    ).exists()

def published_posts_page(page: int) -> QuerySet[Post]:
    """Return 10 published posts for the given page"""
    if page < 1:
        raise ValueError("Page must be 1 or greater")

    start = (page - 1) * 10
    end = start + 10 

    return published_posts() [start:end]

def posts_with_word_in_title(word: str) -> QuerySet[Post]:
    """Find posts containing a word in the title"""
    return Post.objects.filter(title__icontains=word)

def users_with_email_domain(domain: str) -> QuerySet[User]:
    """Find users with the given email domain"""
    return User.objects.filter(
        email__iendswith=f"@{domain}"
    )

def posts_without_category() -> QuerySet[Post]:
    """Return posts without a category"""
    return Post.objects.filter(category__isnull=True)

def categories_by_slugs(slugs: list[str]) -> QuerySet[Category]:
    """Find categories matching the given slugs"""
    return Category.objects.filter(slug__in=slugs)

def posts_in_month(year: int, month: int) -> QuerySet[Post]:
    """Find posts created in the given month"""
    return Post.objects.filter(
        created_at__year=year,
        created_at__month=month,
    )

def posts_last_days(days: int) -> QuerySet[Post]:
    """Find posts created within the last given days"""
    since=timezone.now() - timedelta(days=days)
    return Post.objects.filter(created_at__gte=since)

def posts_between(start: date, end: date) -> QuerySet[Post]:
    """Find posts created between two dates, inclusive"""
    return Post.objects.filter(
        created_at__date__range=(start, end)
    )

def author_published_posts(email: str) -> QuerySet[Post]:
    """Find published posts written by an author"""
    return Post.objects.filter(
        author__email=email,
        status=Post.Status.PUBLISHED,
    )

def posts_with_tag(tag_slug: str) -> QuerySet[Post]:
    """Find posts that have the given tag"""
    return Post.objects.filter(
        tags__slug=tag_slug
    )

def comments_in_category(category_slug: str) -> QuerySet[Comment]:
    """Find comments on posts in the given category"""
    return Comment.objects.filter(
        post__category__slug=category_slug
    )

def users_with_published_posts() -> QuerySet[User]:
    """Find users who have published posts"""
    return User.objects.filter(
        posts__status=Post.Status.PUBLISHED
    ).distinct()

def posts_without_tags() -> QuerySet[Post]:
    """Find posts without any tags"""
    return Post.objects.filter(
        tags__isnull=True
    )

def users_without_comments() -> QuerySet[User]:
    """Find users who have never written comments"""
    return User.objects.filter(
        user_comments__isnull=True
    )

def posts_with_both_tags(
    first_slug: str,
    second_slug: str,
) -> QuerySet[Post]:
    """Find posts containing both specified tags"""
    return Post.objects.filter(
        tags__slug=first_slug
    ).filter(
        tags__slug=second_slug
    ).distinct()

def search_posts(text: str) -> QuerySet[Post]:
    """Search posts by title or body"""
    return Post.objects.filter(
    Q(title__icontains=text) | Q(body__icontains=text)
)

def published_posts_missing_info() -> QuerySet[Post]:
    """Find published posts without a category or tags"""
    return Post.objects.filter(
        Q(category__isnull=True) | Q(tags__isnull=True),
        status=Post.Status.PUBLISHED,
    ).distinct()

def edited_posts() -> QuerySet[Post]:
    """Find posts edited more than one hour after creation"""
    return Post.objects.filter(
        updated_at__gt=F("created_at") + timedelta(hours=1)
    )

def comments_by_post_author() -> QuerySet[Comment]:
    """Find comments written by their posts author"""
    return Comment.objects.filter(
        author=F("post__author")
    )

def comments_before_post() -> QuerySet[Comment]:
    """Find comments created before their posts"""
    return Comment.objects.filter(
        created_at__lt= F("post__created_at")
    )

def published_authors_emails() -> list[str]:
    """Return unique emails of published post authors"""
    return list(
        User.objects.filter(
            posts__status=Post.Status.PUBLISHED
        ).order_by("email").values_list(
            "email", flat=True 
        ).distinct()
    )

def published_post_overview() -> list[dict[str,Any]]:
    """Return published posts with author category information"""
    return list(
        Post.objects.filter(
            status=Post.Status.PUBLISHED
        ).annotate(
            author_email=F("author__email"),
            category_name=Coalesce(
    F("category__name"),
    Value("Uncategorized"),
),
        ).values(
            "title",
            "author_email",
            "category_name",
        )
    )

def posts_stats() -> dict[str,Any]:
    """Return statistics about all posts"""
    return Post.objects.aggregate(
        total=Count("id"),
        published=Count(
            "id",
            filter=Q(status=Post.Status.PUBLISHED),
        ),
        drafts=Count(
            "id",
            filter=Q(status=Post.Status.DRAFT),
        ),
        first_post_at=Min("created_at"),
        last_post_at=Max("created_at"),
    )

def average_comments_per_post() -> float:
    """Return average comments per published post"""
    result = Post.objects.filter(
        status=Post.Status.PUBLISHED
    ).annotate(
        comment_count=Count("comments")
    ).aggregate(
        average=Avg("comment_count")
    )

    return round(result["average"] or 0.0, 2)

def categories_with_post_count() -> QuerySet[Category]:
    """return categories with their number of posts"""
    return Category.objects.annotate(
        post_count=Count("post")
    ).order_by("-post_count", "name")

def categories_with_published_count() -> QuerySet[Category]:
    """Count published posts in each category"""
    return Category.objects.annotate(
        published_count=Count(
            "post",
            filter= Q (post__status=Post.Status.PUBLISHED),
        )
    ).order_by("-published_count", "name")

def top_authors() -> QuerySet[User]:
    """Return the five authors with most published posts"""
    return User.objects.annotate(
        published_count=Count(
            "posts",
            filter=Q(posts__status=Post.Status.PUBLISHED),
        )
    ).filter(
        published_count__gt=0
    ).order_by("-published_count", "email")[:5]

def popular_tags(min_posts: int) -> QuerySet[Tag]:
    """Find tags used by at least min_posts posts"""
    return Tag.objects.annotate(
        post_count=Count("post")
    ).filter(
        post_count__gte=min_posts
    ).order_by("-post_count", "name")

def posts_per_status() -> list[dict[str, Any]]:
    """Count posts grouped by status"""
    return list(
        Post.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

def users_activity() -> QuerySet[User]:
    """Count posts and comments for each user"""
    return User.objects.annotate(
        post_count=Count("posts", distinct=True),
        comment_count=Count("user_comments", distinct=True),
    )

def search_users_by_full_name(text: str) -> QuerySet[User]:
    """Search users by their full name"""
    return User.objects.annotate(
        full_name=Concat(
            F("first_name"),
            Value(" "),
            F("last_name"),
        )
    ).filter(full_name__icontains=text)

def published_posts_per_month() -> QuerySet[Post]:
    """Count published posts by month"""
    return (
        Post.objects.filter(status=Post.Status.PUBLISHED)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

def posts_with_popularity() -> QuerySet[Post]:
    """Label posts based on their comment count"""
    return Post.objects.annotate(
        comment_count=Count("comments")
    ).annotate(
        popularity=Case(
            When(comment_count__gte=10, then=Value("hot")),
            When(comment_count__gte=3, then=Value("normal")),
            default=Value("quiet"),
            output_field=CharField(),
        )
    )

def get_or_create_tag(name: str) -> tuple[Tag, bool]:
    """Get an existing tag or create a new one"""
    return Tag.objects.get_or_create(
        slug=slugify(name),
        defaults={"name": name},
    )

def publish_old_drafts(days: int) -> int:
    """Publish drafts older than the given number of days"""
    now = timezone.now()
    cutoff = now - timedelta(days=days)

    return Post.objects.filter(
        status=Post.Status.DRAFT,
        created_at__lt=cutoff,
    ).update(
        status=Post.Status.PUBLISHED,
        updated_at=now,
    )

def tag_category_posts(category_slug: str, tag_slug: str) -> int:
    """Add a tag to all posts in a category without duplicates"""
    posts = Post.objects.filter(category__slug=category_slug)
    tag = Tag.objects.filter(slug=tag_slug).first()

    if tag is None:
        return 0

    post_ids = posts.values_list("id", flat=True)

    through_model = Post.tags.through
    existing_ids = set(
        through_model.objects.filter(
            post_id__in=post_ids,
            tag_id=tag.id,
        ).values_list("post_id", flat=True)
    )

    new_relations = [
        through_model(post_id=post_id, tag_id=tag.id)
        for post_id in post_ids
        if post_id not in existing_ids 
    ]

    through_model.objects.bulk_create(
        new_relations,
        ignore_conflicts=True,
    )

    return posts.count()

def merge_categories(source_slug: str, target_slug: str) -> int:
    """Move posts to another category and delete the old category"""
    if source_slug == target_slug:
        return 0

    source = Category.objects.filter(slug=source_slug).first()
    target = Category.objects.filter(slug=target_slug).first()

    if source is None or target is None:
        return 0

    moved_count = Post.objects.filter(
        category=source
    ).update(category=target)

    source.delete()

    return moved_count

def delete_inactive_users_comments() -> int:
    """Delete comments written by inactive users """
    comments = Comment.objects.filter(
        author__is_active=False
    )

    deleted_count = comments.count()
    comments.delete()

    return deleted_count

def published_feed() -> list[str]:
    """Return 50 newest published posts as formatted strings"""
    posts = (
        Post.objects.filter(status=Post.Status.PUBLISHED)
        .select_related("author", "category")
        .order_by("-created_at") [:50]
    )

    return [
        f"{post.title} | {post.author.email} | "
        f"{post.category.name if post.category else 'Uncategorized'}"
        for post in posts
    ]

def newest_posts_with_tags() -> list[str]:
    """Return 20 newest posts with their tags"""
    posts = (
        Post.objects.order_by("-created_at")
        .prefetch_related("tags")[:20]
    )

    return [
        f"{post.title}: {', '.join(tag.name for tag in post.tags.all())}"
        for post in posts
    ]

def categories_with_published_posts() -> dict[str, list[str]]:
    """Return categories with their published post titles"""
    published = Post.objects.filter(
        status = Post.Status.PUBLISHED
    ).order_by("-created_at")

    categories = Category.objects.prefetch_related(
        Prefetch("post_set", queryset=published, to_attr="published_posts")
    )

    return {
        category.name: [post.title for post in category.published_posts]
        for category in categories
    }

def posts_with_last_comment() -> QuerySet[Post]:
    """Return published posts with their latest comment"""
    latest_comment = Comment.objects.filter(
        post=OuterRef("pk")
    ).order_by("-created_at")

    return Post.objects.filter(
        status=Post.Status.PUBLISHED
    ).annotate(
        last_comment=Subquery(latest_comment.values("body")[:1])
    )

def posts_with_staff_comments() -> QuerySet[Post]:
    """Return posts that have comments written by staff users"""
    staff_comments = Comment.objects.filter(
        post = OuterRef("pk"),
        author__is_staff=True,
    )

    return Post.objects.annotate(
        has_staff_comments=Exists(staff_comments)
    ).filter(
        has_staff_comments=True
    )

def users_with_draft_as_latest_post() -> QuerySet[User]:
    """Return users whose latest post is a draft"""
    latest_post = Post.objects.filter(
        author=OuterRef("pk")
    ).order_by("-created_at", "-pk")

    return User.objects.annotate(
        latest_post_status=Subquery(
            latest_post.values("status")[:1]
        )
    ).filter(
        latest_post_status=Post.Status.DRAFT
    )

QUERIES = {
    1: categories_by_name,
    2: published_posts,
    3: newest_published_posts,
    4: post_by_slug,
    5: active_users_count,
    6: has_drafts,
    7: published_posts_page,
    8: posts_with_word_in_title,
    9: users_with_email_domain,
    10: posts_without_category,
    11: categories_by_slugs,
    12: posts_in_month,
    13: posts_last_days,
    14: posts_between,
    15: author_published_posts,
    16: posts_with_tag,
    17: comments_in_category,
    18: users_with_published_posts,
    19: posts_without_tags,
    20: users_without_comments,
    21: posts_with_both_tags,
    22: search_posts,
    23: published_posts_missing_info,
    24: edited_posts,
    25: comments_by_post_author,
    26: comments_before_post,
    27: published_authors_emails,
    28: published_post_overview,
    29: posts_stats,
    30: average_comments_per_post,
    31: categories_with_post_count,
    32: categories_with_published_count,
    33: top_authors,
    34: popular_tags,
    35: posts_per_status,
    36: users_activity,
    37: search_users_by_full_name,
    38: published_posts_per_month,
    39: posts_with_popularity,
    40: get_or_create_tag,
    41: publish_old_drafts,
    42: tag_category_posts,
    43: merge_categories,
    44: delete_inactive_users_comments,
    45: published_feed,
    46: newest_posts_with_tags,
    47: categories_with_published_posts,
    48: posts_with_last_comment,
    49: posts_with_staff_comments,
    50: users_with_draft_as_latest_post,
}