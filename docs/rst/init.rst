Initialize Your Project
=======================

Ansible Container provides a convenient way to start your project. Simply run ``ansilbe-container init`` from inside
your project directory.

Here's what *init* creates:

.. code-block:: bash

    ansible
       main.yml
       requirements.txt


main.yml
````````
One of the files found in the ansible directory is main.yml. It's intended to be an example playbook. The plays and
tasks within it are commented out. However, scan through the comments and you'll quickly see that it's an example
playbook for provisioning the containers defined in your application. Use it as a template to build your provisioning
playbook.

requirements.txt
````````````````
Add any Python dependencies required to run your provisioning playbook. When your Ansible build container is created
these dependencies will be installed prior to executing the playbook.








