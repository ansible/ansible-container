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

The ``container.yml`` file is 100% schema compatible with Docker Compose schemas, either version 1 or version 2. Much like
Docker Compose, this file describes the orchestration of your project. Ansible Container uses this file to determine
what images to build, what containers to run and connect, and what images to push to your repository. Additionally, when
Ansible Container generates an Ansible role to ship and orchestrate your images in the cloud, this file describes the
configuration that role ensures is met.

Some entries in the ``container.yml`` file have special meaning and intent that diverge some from vanilla Docker Compose.

1. There must be a container named ``ansible-container``, which represents the builder container. You need only specify for
   the ``command`` value of the name of your Ansible playbook that builds your containers.
2. The ``image`` value for any of the other containers should be the base images you want to start from for the build process.
   Usually this is the official distro image from Docker Hub that you want to use in your containers.

main.yml
````````
In the boilerplate for ``container.yml``, the ``command`` specified for the ``ansible-container`` entry is ``main.yml`` and thus
Ansible has provided an example playbook with that name to build your containers. Ansible Container automatically provides an
inventory with the hosts defined in your ``container.yml`` file. All Ansible features are available, and the ``ansible/``
directory is the proper place to put any roles or modules that your playbook requires.

requirements.txt
````````````````
Running Ansible inside of your build container may have Python library dependencies that your modules require. Use
the ``requirements.txt`` file to specify those dependencies. This file follows the standard `pip <https://pip.pypa.io/>`_
format for Python dependencies. When your Ansible build container is created, these dependencies are installed prior
to executing the playbook.




