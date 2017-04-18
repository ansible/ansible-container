deploy
======

.. program:: ansible-container deploy

The ``ansible-container deploy`` command generates an Ansible role for deploying your app to the cloud. The role is
created based on the configuration found in container.yml

.. option:: --roles-path LOCAL_PATH

**New in version 0.9.0**

If you have Ansible roles in a local path other than your `ansible/` directory that you wish to use
during your build/run/deploy, specify that path with this option.

Immediately after *deploy* specify the cloud service provider. See the :ref:`deploy-engine-idx` for the supported *deploy*
engines. For example, to execute *deploy* with the Kubernetes engine:

.. code-block:: bash

   $ ansible-container --engine k8s deploy


When *deploy* executes it adds a *roles* directory and playbook to the ``ansible-deployment`` directory in the project path.
The playbook it creates will be in the format *<project_name>.yml*.

Subsequent playbook runs will update the playbook and all of the role files as needed.
Each run will create a new tasks playbook. However, each run will also save the previous main.yml
file by appending a timestamp to the file name. If you make changes to the tasks playbook and then run
deploy, your changes will not be lost. They will exist in the most recent timestamped file.


Dependencies
````````````

Execution of the role created by ``deploy`` depends on `Ansible <http://docs.ansible.com/ansible/intro_installation.html>`_
2.3 or greater. Check the specific *deploy* engine for any additional dependencies.

.. _deploy-engine-idx:

Engine Index
````````````
.. toctree::
   :maxdepth: 1

   deploy/kube
   deploy/openshift
