Learn by Example
================

As a learning demonstration, consider the `example <https://github.com/ansible/ansible-container/tree/master/example>`_ provided in the Ansible Container repository that orchestrates
a Django web application with compiled static assets using gulp and Node.js. You
can use Ansible Container to ``build`` and ``run`` this example project, accessing
the orchestrated application on port 80 in your web browser.

The ``container.yml`` file in this example project outlines four services:

.. literalinclude:: ../../example/ansible/container.yml

Each of these containers uses CentOS 7 as its base image.

The production configuration has NGINX as the outward facing web server, serving
the static assets, both collected from the Django project and built by gulp from
sources. That NGINX server proxies requests to Django running under Gunicorn, and
Django uses PostgreSQL as the database backend.

However, in development, it is undesirable to have to rebuild containers every
time lines of code change. Front end developers ordinarily would want
gulp to watch source assets and recompile them upon changes, and
a BrowserSync server to serve them while refreshing the developer's browser
automatically. Back end developers ordinarily would want Django's
built-in web server running instead of Gunicorn, reloading the server upon any
Python source changes.

Because of that, the ``container.yml`` overrides the configuration in the development environment.
NGINX does not expose any ports and exits immediately in the development
environment and, instead, gulp becomes the outward facing webserver, proxying
to Django. This way, containers only have to be rebuilt sporadically, such
as when new dependencies are added or new database migrations are created.

The Ansible playbook to build these services does so looking toward production.

.. literalinclude:: ../../example/ansible/main.yml

Note that the ``host`` specifications use the same names of the services from the
``container.yml`` and rely on the Ansible Container provided inventory to reference
them.

First, the playbook installs Yelp's dumb-init on all of the containers to run as PID 1,
to properly handle SIGTERM, and to reap orphaned processes.

Next, the playbook does a standard setup of Django inside of a Python virtualenv. It
intends for Django to run as a non-superuser, as it does for the other containers as well.
Note that to copy the project's source into the Django container, it runs ``pwd`` in a
pipe, so that the project's directory inside of the Ansible builder container can be
properly resolved.

After setting up PostgreSQL and instructing it to accept authenticated connections
from remote hosts, the playbook runs the Django database migrations. The ``container.yml``
file instructs PostgreSQL to store its data in a local volume, and Ansible Container
uses that volume for both the ``build`` and ``run`` operations.

Django's ``collectstatic`` command gathers static assets bundled with its apps
into a central location for serving. Because NGINX is the desired static file
server, the playbook uses ``find`` to discover those assets and  ``fetch`` to add them
into the Ansible builder container. Because  SSH is not used as a transport, the ``synchronize`` 
module cannot be used.

For the gulp and Node.js container, Ansible installs a copy of Node.js, given that
CentOS 7's version is too dated to be useful for this example. When Ansible Container orchestrates
the project in the development environment, note that it mounts the project
source into the ``/node`` directory. If the playbook installed ``node_modules``
within that path for production use, in development, those modules would be
missing. Therefore, the playbook installs the ``node_modules`` elsewhere to be
preserved for both production and development use. And, like in the Django container,
the playbook needs to ``fetch`` the compiled for delivery to the NGINX container.

Finally, the NGINX container is configured and given a ``copy`` of the Django
and gulp-compiled assets in their proper paths.





