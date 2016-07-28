# Installing Ansible Container

## Prerequisites

Make sure that the following things are installed and available on your system:

* Python 2.7. (This is the standard version for most modern OSes)
* `pip`
* `setuptools`
* Docker 1.11
  * The best way to do this: go to https://www.docker.com/products/docker-toolbox and follow the install instructions.
  * Verify that docker-machine is running: "docker-machine ls" should show a running, active instance called "default".

## Install instructions

The easiest way to install Ansible Container is with the Python package manager, `pip`.

.. code-block:: bash

    $ sudo pip install ansible-container

If you do not have root privileges, you'll need to use a `virtualenv` to create a Python sandbox.

.. code-block:: bash
    
    $ virtualenv ansible-container
    $ source ansible-container/bin/activate
    $ pip install ansible-container

