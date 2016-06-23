build
=====

.. program::ansible-container build

The ``ansible-container build`` command spins up the builder container and runs
your playbook against the base images described in the ``container.yml`` file. At
the end of a successful run of this command, in your container engine you will have
images built for each of the containers in your orchestration. This is analogous to
``docker build``.

.. option:: --flatten

By default, Ansible container commits the changes your playbook made to the base image,
but it retains the original layers from that base image. Specifying this option, Ansible
Container flattens the union filesystem of your image to a single layer.

.. option:: --from-scratch

By default, Ansible Container starts with the last instance of your containers and runs your
playbook against it. That way, if a build fails, you're not starting from zero when rebuilding.
With this option, Ansible Container starts with fresh copies of your base images and
rebuilds from zero.

.. option:: --no-purge-latest

By default, upon successful completion of a build, the previously latest builds for
your hosts are deleted and purged from the engine. Specifying this option, the prior builds
are retained.

.. option:: <ansible_options>

You may also provide additional commandline arguments to give Ansible in executing your
playbook. Use this option with care, as there is no real sanitation or validation of
your input. It is recommended you only use this option to limit the hosts you build
against (for example, if you only want to rebuild one container), to add extra variables,
or to specify tags.

Note that for proper parsing, you will likely have to use ``--`` to separate the
ansible-container options from the ansible-playbook options.

Caveats
```````

Ansible ordinarily connects to hosts it is managing via the SSH protocol. Ansible Container
uses the latest Docker connection plugin to talk to the other containers. Since not all modules
presently function with the Docker connection plugin, it limits the modules your playbook may
rely on. As examples:

* The `become` methods do not work with Ansible Container, as `su` is disallowed in the Docker
  connection plugin (see `#16226 <https://github.com/ansible/ansible/pull/16226>`_)
  and `sudo` requires a TTY. Instead, use the `remote_user` parameter.
* The `synchronize` plugin requires rsync and an ssh transport. Unless you manually install
  ssh and link the ports for that service among your containers, you will have to rely on
  other modules. For example, you can use combinations of `find`, `fetch`, and `copy` to
  achieve similar effects.

Also, remember that the ``ansible-playbook`` executable runs on your builder container, not
your local host, and thus operates in the filesystem and network context of that container.
