shipit
======

.. program:: ansible-container shipit

The ``ansible-container shipit`` command generates an Ansible role to deploy your
project to the cloud and orchestrates those containers according to the directives in
your ``container.yml`` file. While Ansible Container supports multiple different cloud
services, `Red Hat OpenShift <https://www.openshift.com>`_ is recommended.

.. option:: --engine <engine>

This option is required and specifies the cloud service for which a configuration should be generated. Each engine supports its own suboptions. Presently, only ``openshift`` is supported.

OpenShift options
-----------------

.. option:: --save-config

