Accessing Roles
===============

.. contents:: Topics


From the file system
--------------------

Ansible Container provides the ability to add local roles to the Conductor container, and make them available to the ``build`` process,  by using the ``--roles-path`` 
option.

For example, if roles are locally installed in ``/etc/ansible/roles``, the following will make the roles available inside the Conductor container:

.. code-block:: bash

    $ ansible-container build --roles-path /etc/ansible/roles

In ``container.yml``, refer to roles by name. For example, if the role ``apache`` is installed in ``/etc/ansible/roles``
locally, then the following will execute the role during ``build``: 

.. code-block:: yaml
version: '2'
services:
  web:
    roles:
    - apache

From Galaxy and version control
-------------------------------

Ansible Container will automatically install roles included in the ``requirements.yml`` file found in the root of your project directory. If you are unfamiliar with ``requirements.yml``, see `Installing Multiple Roles From a File <http://docs.ansible.com/ansible/galaxy.html#installing-multiple-roles-from-a-file>`_.

Roles are installed to ``/etc/ansible/roles`` on the Conductor container. To run an installed role, simply reference it by name in ``container.yml``.
