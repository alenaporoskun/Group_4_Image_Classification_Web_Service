import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_web_classifier.settings')

application = get_wsgi_application()
app= application
