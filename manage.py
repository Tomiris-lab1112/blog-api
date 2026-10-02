#!/usr/bin/env python
import os, sys
from decouple import config

if __name__ == '__main__':
    env_id = config('BLOG_ENV_ID', default='local')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'settings.env.{env_id}')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
    