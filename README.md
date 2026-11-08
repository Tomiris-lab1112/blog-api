# Blog API — Homework 2

## Project Description

This project is a Django Blog API with a customized Django Unfold administration panel.

## Technologies
- Python
- Django
- Django REST Framework
- Django Unfold
- Faker
- SQLite
## Installation

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements/base.txt
```

## Database Setup
Run migrations:

```powershell
python manage.py migrate
```

Generate sample data:

```powershell
python manage.py seed
```

Generate a specific amount of data:

```powershell
python manage.py seed --users 5 --posts 10 --comments 20
```

Clear existing sample data and generate new data:

```powershell
python manage.py seed --clear
```
## Admin Panel

Create a superuser:

```powershell
python manage.py createsuperuser
```

Start the server:

```powershell
python manage.py runserver
```

Open the admin panel:

http://127.0.0.1:8000/admin/

## Features
- Customized Django Unfold admin interface
- Blog dashboard with statistics
- User management
- Post, Category, Tag and Comment management
- Database seeding using Faker

## Screenshots
Screenshots are available in `docs/screenshots/`