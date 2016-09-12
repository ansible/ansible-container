
Existing Roles
==============

.. contents:: Topics


From the file system
--------------------

Starting with version 0.2.0 Ansible Container provides the ability to add custom volumes to the Ansible Build Container
by using the ``--with-volumes`` option. So if you have roles already installed on the local file system, you can simply
mount the path to the build container.

For example, if roles are installed at /var/roles, the following will make the roles available inside the build container
as ``/roles``:

.. code-block:: bash

    $ ansible-container build --with-volumes /var/roles:/roles

For the roles to be accessed by Ansible Playbook, add an ``ansible.cfg`` file to the ``ansible`` directory, and set the
``roles_path``:

.. code-block:: bash

    [defaults]
    roles_path=/roles

In your ``main.yml`` playbook refer to roles by name. For example, if the role ``geerlingguy.apache`` is installed in /var/roles
locally, then the following will execute the role as part of ``main.yml``:

.. code-block:: yaml

    - name: Example play
      hosts: web
      roles:
        - name: Install apache
          role: geerlingguy.apache

.. note::

    If using Docker Machine, be aware that mounting paths outside fo the user's home directory to a container may
    require additional steps. For more details see the Docker tutorial, `Manage data in containers <https://docs.docker.com/engine/tutorials/dockervolumes/#/mount-a-host-directory-as-a-data-volume>`_.

.. note::

    If you choose to access locally installed roles using ``--with-volumes``, then you must include the same volumes for 
    the ``run`` and ``shipit`` commands as you did for ``build``. During these operations the ``main.yml`` playbook is
    accessed using the ``--list-hosts`` option to determine the list of hosts affected by the playbook. If roles cannot be
    accessed, Ansible Playbook will fail to parse ``main.yml``.


From Galaxy and version control
-------------------------------

Starting in version 0.2.0 Ansible Container will automatically install roles included in a ``requirements.yml`` file placed in
the ``ansible`` directory. If you are unfamiliar with ``requirements.yml``, see `Installing Multiple Roles From a File <http://docs.ansible.com/ansible/galaxy.html#installing-multiple-roles-from-a-file>`_.

The default ``roles_path`` is set to ``/etc/ansible/roles`` on the build container, and roles will be installed there. No special
changes are required in ``main.yml``. To run an installed role simply refer to it by name.


Making roles *container safe*
-----------------------------

If you're new to managing the application lifecycle through containers, it's almost certain that any roles you've written in the
past were not written from the perspective of running inside a container and with the intent of producing a container image.
Making a role *container safe* is just a name for the process of reviewing a role and disabling or removing tasks that won't work
or don't make sense in a containerized infrastructure.

Here are some things to consider and review before attempting to build an image with an existing Ansible role:

Eliminate what doesn't work
```````````````````````````

Sometimes things just don't work in a container. For example, unless the container has an init system, the ``service`` module
will not work. Lots of roles install a software package and then either as a final task or by way of a handler, call the ``service``
module to start and enable the newly installed service. In cases like this, where you know the module will not work in a container,
you can completely remove it, or you can disable for containers by testing ``ansible_connection``. If the task is being executed
through the Docker connection plugin, it will be set to ``docker``.

For example, the following will only call the ``service`` module to start the apache service if ``ansible_connection`` is not equal
to ``docker``:

.. code-block:: yaml

    - name: Start and enable apache
      service: name=apache state=restarted enabled=yes
      when: ansible_connection != 'docker'

Ansible Container relies on the Docker connection plugin to communicate from the build container to the containers making up
the application, so all of the tasks and roles in ``main.yml`` will have ``ansible_connection`` set to ``docker``.

Clean up the filesystem
```````````````````````

Another thing to consider when executing a role within a container is the size of the final image. Ansible Container starts with
a base image and adds a layer to it. What's in that layer is the result of all the tasks executed in ``main.yml``, including any files
downloaded or copied files.

Lots of tasks download archive files, especially package managers, and either keep them in a cache directory or never clean up
after themselves. This might be OK and even beneficial within a virtual machine, but within a container it will produce a bloated image.

Check the package manager you're using, and as a final step to updating and installing packages, run the command that cleans up the
cache. In the case of Yum, you might do the following:

.. code-block:: yaml

    - name: Update all packages
      yum: name=* state=latest

    - name: Install mysql
      yum: name=mysql-server state=present

    - name: Purge yum cache
      command: yum clean all

Another culprit is get_url. Make sure any .rpm or .deb files are removed after installation. For example, installing filebeat in a
Debian container might look like the following:

.. code-block:: yaml

    - name: Download filebeat
      get_url: url=https://download.elastic.co/beats/filebeat/filebeat_1.0.1_amd64.deb dest=/filebeat_1.0.1_amd64.deb mode=0664

    - name: Install filebeat
      apt: deb=/filebeat_1.0.1_amd64.deb

    - name: Remove package file
      file: path=/filebeat_1.0.1_amd64.deb state=absent


Run a single service only
`````````````````````````

A production container can only execute a single service. Many roles are written to run a stack of services. Take for example
the LAMP stack. A role will typically install Apache, MySQL and possibly supporting services like iptables. That works great
for a virtual machine, however a container is intended to run only a single service. What we really need is two roles, one for
Apache and a completely separate role for MySQL. So if you have roles like this, you'll need to split them apart into multiple
roles.

Make images that don't require root
```````````````````````````````````

A production container never executes as the root user. When we're building a container for the purpose of creating an image,
it's OK to run as root, but any container created from the resulting image should not run as root.

It's very likely that your existing roles do not take this into account as Virtual machines generally start processes as root
and then ``su`` to a user account. Take the case of MySQL. On a Centos 7 virtual machine you would start the process by running:
``sudo systemctl start mysqld``. This will invoke an init script as root, do any pre-launch tasks, and then launch the mysqld
process as the mysql user.

A role tasked with installing and configuring MySQL within a container should include setting file system permissions so that
everything in the final image can be executed as a non-privileged user.

Be careful with credentials
```````````````````````````

Remove any tasks that write credentials to the filesystem. For example, you might have a role that creates a ``.pgpass`` file,
making it possible to access a Postgresql database without a password. To avoid accidentally exposing passwords, define
environment variables in your ``container.yml`` and provide the values using ``--var-file`` or environment variables:

In ``container.yl`` you might have the following:

.. code-block:: yaml

    services:
        web:
            environment:
                - POSTGRES_USERNAME={{ postgres_username }}
                - POSTGRES_PASSWORD={{ postgres_password }}

In a variable file called `develop.yml`, you could provided the username and password values:

.. code-block:: yaml

    ---
    postgres_username: admin
    postgres_password: mypassword


.. code-block:: bash

Then pass in the variable file using ``--var-file``:

    $ ansible-container --var-file develop.yml build

Or as an alternative to a variable file, pass in the values using ``AC_`` environment variables:

.. code-block:: bash

    $ export AC_POSTGRES_USERNAME=admin
    $ export AC_POSTGRES_PASSWORD=mypassword
    $ ansible-container build

Be immutable
````````````

Containers are meant to be immutable, which means log files and data should `not` be be stored on the container's filesystem. A
role author should therefore think about configuring the service in such a way that it's easy for an image user to mount
custom volumes to collect log files and data, and if necessary makes changes to how and where data is written simply by setting
environment variables.

Don't rely on IP addresses
``````````````````````````

Virtual machines generally have a hostname that doesn't change and often times a static IP address, so an entry
in ``/etc/hosts`` is all that's needed to facilitate communication. A container's IP address and possibly it's name will change
every time it gets restarted or recreated, so communication is facilitated by way of environment variables. An application
within a container will typically get the name of a host and port by looking at environment variables. Make sure your role is
not adding entries to ``/etc/hosts`` or hard-coding container names and IP addresses into configuration files.
