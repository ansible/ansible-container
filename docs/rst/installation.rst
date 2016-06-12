Installation
============

.. contents:: Topics

.. _getting_ansible_container:

Getting Ansible Container
`````````````````````````

Since this project is in pre-release, the best option for obtaining Ansible Container is to run from source.

.. _running_from_source:

Running from Source
```````````````````
Prerequisites:

* Python 2.7
* `Git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_
* `Docker <https://docs.docker.com/engine/installation/>`_ or access to a Docker daemon

If you're installing Docker Engine or accessing a remote Docker daemon, see :ref:`configure_docker`.

Clone the repo:

.. code-block:: bash

    $ git clone git@github.com:ansible/ansible-container.git

If you just want to run ansible-container:

.. code-block:: bash

    $ cd ansible-container
    $ python ./setup.py install

Or, if you plan to help develop ansible-container:

.. code-block:: bash

    $ cd ansible-container
    $ python ./setup.py develop

.. _configure_docker:

Configuring Docker
``````````````````
If you're using Docker Machine, you can skip this section. Otherwise, to use ansible-container, you'll need Docker
Engine installed and configured for TCP access or access to a remote Docker daemon.

.. _docker_engine:

Docker Engine
-------------
After `installing Docker engine <https://docs.docker.com/engine/installation/>_` the daemon is accessible via a Unix
socket that restricts access to the local root user. Using ansible-container requires changing this so that the Docker
daemon is accessible via TCP.

You can simply change the -H option in the startup options of the Docker daemon service, setting it to
*tcp://<host IP address>:2376* and giving access to everyone. This is *NOT recommended* because it will be
trivial for anyone to gain root access to the host. Instead, we recommend securing the Docker daemon.
See :ref:`secure_docker` below.

For ansible-container to work the Docker daemon must be set to listen on an IP address assigned to the host *NOT*
0.0.0.0 or 127.0.0.1. This is because the daemon must be accessible remotely from the Ansible build container.

Client Access
-------------

To access the Docker daemon define the DOCKER_HOST environment variable in the user's environment so that it matches the
-H setting of the Docker daemon:

.. code-block:: bash

    DOCKER_HOST=tcp://<host IP address>:2376

As mentioned above in :ref:`docker_engine` the daemon must be accessible via TCP.

**NOTE** ansible-container requires DOCKER_HOST to be defined in the user's environment.

.. _secure_docker:

Securing Docker Daemon
----------------------
To secure the Docker daemon you will need the following:

* openssl
* ansible (optional)

Use the `ansible.secure-docker-daemon <https://galaxy.ansible.com/ansible/secure-docker-daemon/>`_ Galaxy role to
generate the certificates. Instructions for using the role and a sample playbook are provided in the README. You can
also generate the certificates manually by following the
`instructions here <https://docs.docker.com/engine/security/https/>`_.

Once the certificates are generated, copy the client certificate, key and CA certificate to $HOME/.docker for any user
accessing the Docker daemon or running ansible-container. Set access permissions on the files so that only the user can
access them.

Copy the server certificate, key and CA certificate to the daemon host, if they were not generated on the host. On a
Linux host these files will typically be placed in /etc/docker. Set the file permissions so that only the root user has
access. Modify the Docker daemon startup options to use TLS and load the server certificates. How you modify the daemon
startup options will depend on your environment. Set the following options and restart the service:

* --tlsverify
* --tlscacert=/path/to/ca.pem
* --tlscert=/path/to/server-cert.pem
* --tlskey=/path/to/server-key.pem
* -H=tcp://<host IP address>:2376

For client access to the daemon, set the following variables in the user environment:

* DOCKER_TLS_VERIFY=1
* DOCKER_HOST=tcp://<host IP address>:2376

For ansible-container to access the client certificates, set the following variable in the user's environment:

* DOCKER_CERT_PATH=/path/to/certs

For convenience the ansible.secure-docker-daemon Galaxy role generates a small shell script called docker_env.sh that
can be used in a Linux environment to define the above variables.









