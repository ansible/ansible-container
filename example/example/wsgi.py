"""
WSGI config for example project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

import socket
import time

postgres_is_alive = False
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while not postgres_is_alive:
    try:
        s.connect(('postgresql', 5432))
    except socket.error:
        time.sleep(1)
    else:
        postgres_is_alive = True
 

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

application = get_wsgi_application()
