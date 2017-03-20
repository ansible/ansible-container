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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

application = get_wsgi_application()
