Initialize Your Project
=======================

Ansible Container provides a convenient way to start your project by simply running ``ansilbe-container init`` from inside
your project directory.

Here's what ``init`` creates:

.. code-block:: bash

    ansible
       main.yml
       requirements.txt


main.yml
````````
One of the files found in the ansible directory is ``main.yml``. It is intended to be an example playbook. The plays and
tasks within it are commented out. However, by scanning through the comments, you can see that ``main.yml`` provides an example
playbook for provisioning the containers defined in your application. Use it as a template to build your own provisioning
playbook.

requirements.txt
````````````````
Add any Python dependencies required to run your provisioning playbook. When your Ansible build container is created,
these dependencies are installed prior to executing the playbook.








