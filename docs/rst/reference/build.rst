build
=====

.. program::ansible-container build

The ``ansible-container build`` command spins up the builder container and runs
your playbook against the base images described in the ``container.yml`` file. At
the end of a successful run of this command, you will have in your container engine
built images for each of the containers in your orchestration. This is analogous to
``docker build``.

.. option:: --no-flatten

By default, Ansible Container will flatten the union filesystem of your image to
a single layer. Specifying this option, Ansible container will commit the changes
your playbook made to the base image, but it will retain the original layers from
that base image.

.. option:: --rebuild

By default, Ansible Container will start fresh from the base image and run your
playbook against it, regardless of whether you've already built these images before.
With this option, Ansible Container will start with the latest build of your images
already committed to the engine, and then it will rerun your playbook over them. On
one hand, this will result in faster rebuilds. On the other hand, this will add
additional committed layers to the union filesystem.

.. option:: --no-purge-latest

By default, upon successful completion of a build, the previously latest builds for
your hosts will be deleted and purged from the engine. Specifying this option, they
will be retained.

