shipit
======

.. program:: ansible-container shipit

The ``ansible-container shipit`` command generates an Ansible role for deploying your app to the cloud. The role is
created based on the configuration found in container.yml

Immediately after *shipit* specify the cloud service provider. See the :ref:`shipit-engine-idx` for the supported *shipit*
engines. For example, to execute *shipit* with the Kubernetes engine:

.. code-block:: bash

   $ ansible-container shipit kube


When *shipit* executes it adds a *roles* directory and playbook to the ansible directory, and within
the *roles* directory it creates an Ansible role. The role name will be in the format *<project_name>-<shipit_engine>*.
The playbook name will be in the format *shipit-<shipit_engine>.yml*.

Subsequent playbook runs will leave the playbook and all of the role files untouched with the exception of
*tasks/main.yml*. Each run will create a new tasks playbook. However, each run will also save the previous main.yml
file by appending a timestamp to the file name. If you make changes to the tasks playbook and then run
shipit, your changes will not be lost. They will exist in the most recent timestamped file.


Dependencies
````````````

Execution of the role created by ``shipit`` depends on `Ansible <http://docs.ansible.com/ansible/intro_installation.html>`_
2.0 or greater. Check the specific *shipit* engine for any additional dependencies.

.. _shipit-engine-idx:

Engine Index
````````````
.. toctree::
   :maxdepth: 1

   shipit/kube
   shipit/openshift