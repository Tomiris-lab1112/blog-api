
from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "post_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _post_count=Count("post")
        )

    @display(description="Posts", ordering="_post_count")
    def post_count(self, obj):
        return obj._post_count


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug", "post_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _post_count=Count("post")
        )

    @display(description="Posts", ordering="_post_count")
    def post_count(self, obj):
        return obj._post_count


class CommentInline(TabularInline):
    model = Comment
    extra = 0
    fields = ("author", "body")
    autocomplete_fields = ("author",)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "status_label",
        "created_at",
        "comment_count",
    )

    list_filter = (
        "status",
        "category",
        "created_at",
    )

    search_fields = (
        "title",
        "body",
        "author__email",
    )

    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author", "category", "tags")
    list_select_related = ("author", "category")
    list_per_page = 25

    inlines = (CommentInline,)

    actions = ("publish_posts", "make_drafts")

    fieldsets = (
        (
            "Content",
            {
                "fields": ("title", "slug", "body"),
                "classes": ("tab",),
            },
        ),
        (
            "Organization",
            {
                "fields": ("author", "category", "tags"),
                "classes": ("tab",),
            },
        ),
        (
            "Publishing",
            {
                "fields": ("status",),
                "classes": ("tab",),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _comment_count=Count("comments", distinct=True)
        )

    @display(
        description="Status",
        label={
            "published": "success",
            "draft": "warning",
        },
    )
    def status_label(self, obj):
        return obj.status

    @display(description="Comments", ordering="_comment_count")
    def comment_count(self, obj):
        return obj._comment_count

    @admin.action(description="Publish selected posts")
    def publish_posts(self, request, queryset):
        count = queryset.update(status="published")
        self.message_user(
            request,
            f"{count} posts published."
        )

    @admin.action(description="Move selected posts to drafts")
    def make_drafts(self, request, queryset):
        count = queryset.update(status="draft")
        self.message_user(
            request,
            f"{count} posts moved to drafts."
        )


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = (
        "post",
        "author",
        "short_body",
        "created_at",
    )

    search_fields = (
        "body",
        "post__title",
        "author__email",
    )

    autocomplete_fields = ("post", "author")
    list_select_related = ("post", "author")
    list_filter = ("created_at",)

    @display(description="Comment")
    def short_body(self, obj):
        if len(obj.body) > 60:
            return obj.body[:60] + "..."
        return obj.body
