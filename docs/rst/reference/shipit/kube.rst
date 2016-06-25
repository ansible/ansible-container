kube
====

.. program:: ansible-container shipit kube

The ``ansible-container shipit kube`` command creates an Ansible playbook and role to deploy your
application on Kubernetes. The playbook and role are created in the ansible directory. The name of the playbook
is *shipit-kubernetes.yml*, and the name of the role is *<project_name>-kubernetes* and can be found in the
roles directory.

.. option:: --help

Display usage help.

.. option:: --save-config

In addition to creating the playbook and role, creates a *shipit_config/kubernetes* directory and writes out each
JSON config file used to create the Kubernetes services and deployments for your application.

.. option:: --pull-from <registry name>

Pass either a name defined in the *registries* key within container.yml or the actual URL the cluster will use to
pull images. If passing a URL, an example would be 'registry.example.com:5000/myproject'.






