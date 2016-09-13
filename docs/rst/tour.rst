Quick Tour
============

Ansible Container provides a convenient way to start your project by simply running ``ansible-container init`` from within
your project directory.

Running ``init`` creates the following:

.. code-block:: bash

    ansible/
       container.yml
       main.yml
       requirements.txt

These are merely boilerplate files, but should be enough to get you started.

container.yml
`````````````
The ``container.yml`` file is the heart of Ansible Container.

The ``container.yml`` file is very similar to the Docker Compose version 1 schema. Much like
Docker Compose, this file describes the orchestration of your project. Ansible Container uses this file to determine
what images to build, what containers to run and connect, and what images to push to your repository. Additionally, when
Ansible Container generates an Ansible role to ship and orchestrate your images in the cloud, this file describes the
configuration that role ensures is met.

By way of an example, consider the below ``container.yml`` file:

.. code-block:: yaml

    version: "1"
    services:
      web:
        image: "ubuntu:trusty"
        ports:
          - "80:80"
        command: ["/usr/bin/dumb-init", "/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
        dev_overrides:
          environment:
            - "DEBUG=1"

Things to note:

1. We mark this schema with version 1. Future versions may deviate from this schema.
2. Each of the containers you wish to orchestrate should be under the `services` key.
3. The content of the `services` key observes all of the keys supported by the
   Docker Compose v1 schema.
4. The image you specify should be the base image that your containers will start from.
   Ansible Container will use your playbook to build upon this base image.
5. You may optionally specify a `dev_overrides` section. During build and in generating
   the Ansible roles to deploy your application to the cloud, this section will be
   ignored. However, when running your containers locally for your development environment,
   you may use this section to override settings from your production configuration. For
   instance, a Javascript developer may wish to use Gulp and BrowserSync to dynamically
   rebuild assets while development is taking place, versus rebuilding the entire container
   for every code change. Thus that developer may wish to include dev_overrides that run
   a BrowserSync server for those assets, whereas in production Gulp would build those assets
   and exit.

main.yml
````````

The ``main.yml`` file contains the playbook to use in building your containers. Ansible Container automatically provides an
inventory with the hosts defined in your ``container.yml`` file. All Ansible features are available, and the ``ansible/``
directory is the proper place to put any roles or modules that your playbook requires.

For convenience the environment variable ``ANSIBLE_CONTAINER=1`` is set in any containers where ``main.yml`` executes. This
may be useful in roles or includes where task execution needs to be conditional. For example:

.. code-block:: yaml

  - name: Only say hello when running via Ansible Container
    command: echo "Hello!"
    when: ansible_env.ANSIBLE_CONTAINER is defined

Visit `Ansible Roles </ansible-container/roles/index.html>`_ for best practices around writing and using roles within
Ansible Container.

requirements.txt
````````````````
Running Ansible inside of your build container may have Python library dependencies that your modules require. Use
the ``requirements.txt`` file to specify those dependencies. This file follows the standard `pip <https://pip.pypa.io/>`_
format for Python dependencies. When your Ansible build container is created, these dependencies are installed prior
to executing the playbook.

requirements.yml
````````````````
If your playbook has role dependencies, and you want the roles automatically installed from Galaxy or directly from
version control, add them to ``requirements.yml``. For more information about ``requirements.yml`` see
`Installing Roles From a File <http://docs.ansible.com/ansible/galaxy.html#installing-multiple-roles-from-a-file>`_.

Roles are installed to the default ``roles_path``, ``/etc/ansible/roles``. If needed, you can override this by updating
``ansible.cfg``.

ansible.cfg
```````````
Set Ansible configuration settings within the build container. For more information see `Configuration File <http://docs.ansible.com/ansible/intro_configuration.html`_.




