build
=====

.. program::ansible-container build

The ``ansible-container build`` command spins up the builder container and runs
your playbook against the base images described in the ``container.yml`` file. At
the end of a successful run of this command, in your container engine you will have
images built for each of the containers in your orchestration. This is analogous to
``docker build``.

.. option:: --no-flatten

By default, Ansible Container flattens the union filesystem of your image to
a single layer. Specifying this option, Ansible container commits the changes
your playbook made to the base image, but it retains the original layers from
that base image.

.. option:: --rebuild

By default, Ansible Container starts fresh from the base image and runs your
playbook against it, regardless of whether you've already built these images before.
With this option, Ansible Container starts with the latest build of your images
already committed to the engine, and then it reruns your playbook over them. On
one hand, this results in faster rebuilds. On the other hand, this adds
additional committed layers to the union filesystem.

.. option:: --no-purge-latest

By default, upon successful completion of a build, the previously latest builds for
your hosts are deleted and purged from the engine. Specifying this option, the prior builds
are retained.

