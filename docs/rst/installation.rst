Installation
============

.. contents:: Topics

.. _getting_ansible_container:

Getting Ansible Container
`````````````````````````

Because this software project is still in pre-release, the best option for obtaining Ansible Container is to run it from source.

.. _running_from_source:

Running from Source
```````````````````
First, you must have python 2.7 and `git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_. You also need to have
access to a Docker daemon, which may require installing Docker or Docker Machine.

It is also recommended that you install Ansible Container within a Python `virtualenv <https://virtualenv.pypa.io/en/stable/>`_.

Clone the repo:

.. code-block:: bash

    $ git clone git@github.com:ansible/ansible-container.git

Install prerequisites using the requirements file in your local ansible-container repo:

.. code-block:: bash

    $ cd ansible-container
    $ pip install -r requirements.txt

Install ansible-container:

.. code-block:: bash

    $ python ./setup.py install









