"""
WSGI config for django_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
application = get_wsgi_application()

# ✅ Add this block to create superuser if none exists
# from django.contrib.auth import get_user_model
# User = get_user_model()
# try:
#     if not User.objects.filter(is_superuser=True).exists():
#         User.objects.create_superuser(
#             username='admin',  # Change to your preferred username
#             email='admin@example.com',  # Change to your email
#             password='admin123'  # Change this!
#         )
#         print("Superuser created successfully!")
# except Exception as e:
#     print(f"Error creating superuser: {e}")



