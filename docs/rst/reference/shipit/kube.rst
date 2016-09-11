kube
====

.. program:: ansible-container shipit kube

The ``ansible-container shipit kube`` command creates an Ansible playbook and role to deploy your
application on Kubernetes. The playbook and role are created in the ansible directory. The name of the playbook
is *shipit-kubernetes.yml*, and the name of the role is *<project_name>-kubernetes* and can be found in the
roles directory.

.. note::

    Before ``shipit`` starts, the build container is started, and Ansible Playbook is
    invoked with the ``--list-hosts`` option to inspect ``main.yml`` and return the list of hosts
    it touches. When entering the ``run`` command supply the same ``--with-volumes`` and
    ``--with-variables`` options passed to the``build`` command. This will ensure that ``main.yml``
    can be parsed and interpreted.

.. option:: --help

Display usage help.

.. option:: --save-config

In addition to creating the playbook and role, creates a *shipit_config/kubernetes* directory and writes out each
JSON config file used to create the Kubernetes services and deployments for your application.

.. option:: --pull-from <registry name>

Pass either a name defined in the *registries* key within container.yml or the actual URL the cluster will use to
pull images. If passing a URL, an example would be 'registry.example.com:5000/myproject'.

.. option:: --with-variables WITH_VARIABLES [WITH_VARIABLES ...]

**New in version 0.2.0**

Define one or more environment variables in the Ansible Builder Container. Format each variable as a
key=value string.

.. option:: --with-volumes WITH_VOLUMES [WITH_VOLUMES ...]

**New in version 0.2.0**

Mount one or more volumes to the Ansible Builder Container. Specify volumes as strings using the Docker
volume format.



