from typing import Any 
from django.core.management.base import BaseCommand, CommandParser 
from django.contrib.auth.hashers import make_password
from django.core.management.base import CommandError
from faker import Faker 
from django.utils.text import slugify 

import random 

from apps.blog.models import Category, Comment, Tag, Post

from apps.auths.models import User 

DEFAULT_USERS=20
DEFAULT_POSTS=100
DEFAULT_COMMENTS=500 

SEED_PASSWORD="TestPassword123!"
INACTIVE_PERCENT=0.15
STAFF_PERCENT=0.10

PUBLISHED_PERCENT = 0.70
NO_CATEGORY_PERCENT= 0.10
MAX_TAGS_PER_POST = 5 
POST_PARAGRAPHS = 3 

MIN_COMMENT_SENTENCES = 1 
MAX_COMMENT_SENTENCES = 3 

CATEGORY_NAMES = [
    "Python",
    "Django",
    "DevOps",
    "Frontend",
    "Backend",
    "Databases",
    "Security",
    "Artificial Intelligence",
]

TAG_NAMES = [
    "Tutorial",
    "Beginner",
    "Advanced",
    "API",
    "REST",
    "Docker",
    "Git",
    "GitHub",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Vue",
    "SQL",
    "PostgreSQL",
    "Testing",
    "Deployment",
    "Cloud",
    "Machine Learning",
    "Best Practices",
]

class Command(BaseCommand):
    help = "Fill the database with fake data"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--users", type=int,default=DEFAULT_USERS)
        parser.add_argument("--posts", type=int,default=DEFAULT_POSTS)
        parser.add_argument("--comments", type=int,default=DEFAULT_COMMENTS)
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        users_count=options["users"]
        posts_count=options["posts"]
        comments_count=options["comments"]
        clear = options ["clear"]

        if min(users_count, posts_count, comments_count)<0:
            raise CommandError("Counts cannot be negative.")

        if clear:
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()

        fake = Faker()
        hashed_password=make_password(SEED_PASSWORD)

        existing_emails=set(
            User.objects.values_list("email",flat=True)
        )

        users_to_create=[]

        while len(users_to_create) < users_count:
            first_name= fake.first_name()
            last_name= fake.last_name()

            email = (
                f"{first_name}.{last_name}@example.com"
                .lower()
                .replace(" ", "")
            )

            if email in existing_emails:
                continue

            existing_emails.add(email)

            users_to_create.append(
                User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=hashed_password,
                    is_active=fake.pyfloat() >= INACTIVE_PERCENT,
                    is_staff=fake.pyfloat() < STAFF_PERCENT,
                )
            )
        User.objects.bulk_create(users_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f"Users: {len(users_to_create)} created"
            )
        )

        categories_created=0

        for name in CATEGORY_NAMES:
            slug = slugify(name)

            if not Category.objects.filter(slug=slug).exists():
                Category.objects.create(
                    name=name,
                    slug=slug,
                )
                categories_created += 1 

        tags_created = 0 

        for name in TAG_NAMES:
            slug = slugify(name)

            if not Tag.objects.filter(slug=slug).exists():
                Tag.objects.create(
                    name=name,
                    slug=slug,
                )
                tags_created += 1 

        self.stdout.write(
            self.style.SUCCESS(
                f"Categories: {categories_created} created"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Tags: {tags_created} created"
            )
        )

        all_users= list(User.objects.all())
        all_categories = list(Category.objects.all())
        all_tags = list(Tag.objects.all())

        if posts_count > 0 and not all_users:
            raise CommandError("Cannot create posts without users.")

        existing_slugs = set(
            Post.objects.values_list("slug", flat = True )
        )

        posts_to_create = []
        for _ in range(posts_count):
            title=fake.sentence(nb_words=6).rstrip(".")
            base_slug= slugify(title)
            slug=base_slug
            suffix=2

            while slug in existing_slugs:
                slug= f"{base_slug}-{suffix}"
                suffix += 1 

            existing_slugs.add(slug)

            category = None 

            if all_categories and random.random() >= NO_CATEGORY_PERCENT:
                category = random.choice(all_categories)

            status = (
                "published"
                if random.random() < PUBLISHED_PERCENT
                else "draft"
            )

            posts_to_create.append(
                Post(
                    author=random.choice(all_users),
                    title=title,
                    slug=slug,
                    body= "\n\n".join(fake.paragraphs(nb=POST_PARAGRAPHS)),
                    category=category,
                    status=status,
                )
            )
        Post.objects.bulk_create(posts_to_create)

        for post in posts_to_create:
            number_of_tags= random.randint(
                0, min(MAX_TAGS_PER_POST, len(all_tags))
            )
            post.tags.set(
                random.sample(all_tags, number_of_tags)
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Posts: {len(posts_to_create)} created"
            )
        )

        published_posts= list (
            Post.objects.filter(status="published")
        )

        if comments_count > 0 and not all_users:
            raise CommandError(
                "Cannot create comments without users."
            )
        if comments_count > 0 and not published_posts:
            raise CommandError(
                "Cannot create comments without published posts."
            )

        comments_to_create = []

        for _ in range(comments_count):
            sentences_count = random.randint(
                MIN_COMMENT_SENTENCES,
                MAX_COMMENT_SENTENCES,
            )

            comments_to_create.append(
                Comment(
                    post=random.choice(published_posts),
                    author=random.choice(all_users),
                    body=" ".join(
                        fake.sentences(nb=sentences_count) 
                    ),
                )
            )

        Comment.objects.bulk_create(comments_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f"Comments: {len(comments_to_create)} created"
            )
        ) 