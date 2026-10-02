from decouple import config

ENV_ID: str = config('BLOG_ENV_ID', default='local')
SECRET_KEY: str = config('BLOG_SECRET_KEY', default='django-insecure-secret-key-12345')
DEBUG: bool = config('BLOG_DEBUG', default=True, cast=bool)