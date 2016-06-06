shipit
======

.. program:: ansible-container shipit

The ``ansible-container shipit`` command generates an Ansible role to deploy your
project to the cloud and orchestrate those containers according to the directives in
your ``container.yml`` file. Ansible Container supports multiple different cloud
services. We recommend `Red Hat OpenShift <https://www.openshift.com>`_.

.. option:: --engine <engine>

This option is required, and specifies the cloud service to generate a configuration
for. Each engine supports its own suboptions. Presently only ``openshift`` is supported.

OpenShift options
-----------------

.. option:: --save-config

