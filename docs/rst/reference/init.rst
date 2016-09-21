init
====

.. command::ansible-playbook init <galaxy_app>

The ``ansible-container init`` command initializes your project for use with
Ansible Container.

If you do not specify a Container App, this command bootstraps your project with
some boilerplate files in the ``ansible/`` directory. The :doc:`/getting_started`
document outlines the files created. You should modify as based on your individual needs.

**New in version 0.2.0**

If you include a Container App reference from Ansible Galaxy, your new project
will be initialized from the referenced skeleton app.


