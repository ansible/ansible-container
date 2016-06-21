shipit
======

.. program:: ansible-container shipit

The ``ansible-container shipit`` command generates an Ansible role to deploy your
project to the cloud and orchestrate the project's containers according to the directives
in your ``container.yml`` file. Use the ``--engine`` option to choose a cloud provider.

When shipit executes, it will create a ``roles`` directory in your project, and within
the ``roles`` directory a role matching your project's name. Within your project directory
it also creates a sample playbook called ``shipit.yml`` to execute the role.

Running the ``shipit`` command multiple time will overwrite the shipit.yml playbook
and the contents of the role. Be careful, if you modify any of the files created by
``shipit``.

.. option:: --engine <engine>

Specify the cloud service provider to use. Defaults to `Red Hat OpenShift <https://www.openshift.com>`.
Presently, only ``openshift`` is available.

.. option:: --save-config

Save the raw cloud deployment files. These files will be written to a new directory called ``shipt_config``
created in your project directory.

OpenShift
---------

To communicate with OpenShift and deploy your application, the role produced by ``shipit`` includes custom
modules copied into the ``roles/<your project name>/library`` path. These modules are currently only found in
the ansible-container project. They are not part of the Ansible project. In the future these modules may be
replaced by modules delivered by the Ansible project. Keep this in mind, if you begin modifying the role.

Dependencies
````````````

Execution of the role created by ``shipit`` depends on:

- `Ansible <http://docs.ansible.com/ansible/intro_installation.html>` 2.0 or greater on the control node.
- `OpenShift Origin 3 <https://www.openshift.org/>` or greater. The role will not work with
  `OpenShift Online <https://www.openshift.com/>`.
- The `OpenShift command line client <https://docs.openshift.org/latest/cli_reference/get_started_cli.html>`
  must be installed on the Ansible target nodes. Be sure the verion of the installed client supports the target
  OpenShift cluster version.
