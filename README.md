# Blog API - Homework 2 & 3

This is my Django Blog API project.

## Technologies
- Python
- Django
- Django REST Framework
- Django Unfold
- SQLite
- Faker

## How to Run

Install requirements:
```
pip install -r requirements/base.txt
```

Run migrations:
```
python manage.py migrate
```

Create sample data:
```
python manage.py seed
```

Start the server:
```
python manage.py runserver
```

## Homework 3 - ORM Queries

I created 50 Django ORM queries to work with posts, users, comments, categories, and tags.

Run all read-only queries:
```
python manage.py queries
```

Run one query:
```
python manage.py queries --number 31
```

Show SQL:
```
python manage.py queries --number 31 --sql
```

Queries 40-44 change database data, so they should be used carefully.

## Features
Django admin panel
Blog models
Sample data with Faker
50 ORM queries
Filtering and searching
Aggregation and annotations
Database updates