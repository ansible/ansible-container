Galaxy Integration
==================

`Ansible Galaxy <https://galaxy.ansible.com/>`_ is the public commons for Ansible roles,
and it now includes support for container-enabled roles and container app skeletons.

Container-Enabled Roles
-----------------------

Since container best-practices center around one process/service per container, and since
Ansible Roles generally encompass a single function, there's a natural harmony between them.
Container-enabled roles are normal Ansible roles that integrate easily with an Ansible Container
project.

A container-enabled role is one that defines a containerizable service. It contains a file
``meta/container.yml`` in it, containing a sane default service configuration for adding
the container to ``ansible/container.yml``. While these files are named the same, the
``container.yml`` in a container-enabled role only contains the service definition, not
the rest of a complete ``container.yml``, much the same way that other files in an Ansible
role are a subset of a complete playbook.

Container-enabled roles are best added to your project using the :doc:`ansible-container install </reference/install>`
command, which will add the role to your ``ansible/requirements.yml`` and modify your
``ansible/container.yml`` and ``ansible/main.yml`` to build and run the service the role
defines.

Container Apps
--------------

While container-enabled roles work well for bolt-on services, they do not work well for
multi-container orchestration; a role can only truly define a single container service.

Ansible Galaxy also hosts *container apps*, which are skeletons of complete Ansible Container
projects, useful for bootstrapping new projects. For example, a single web-page application
talking to a JBoss backend would need a node.js server to compile static assets, a JBoss application
server, and one or more databases like MySQL or MongoDB - at least three containers, orchestrated
together. A container app provides the skeleton to get started with these sorts of stacks.

A container app is not a role. It contains an ``ansible/`` directory, complete with ``container.yml``,
``main.yml``, and ``requirements.yml``. It may even bundle its own roles in ``ansible/roles/`` or
refer to container-enabled roles on Galaxy using ``requirements.yml``. It can also include source code
files useful for developing your specific project, like a ``Gulpfile.js`` or a ``package.json``.

Container apps are best used by, in an empty project directory, running :doc:`ansible-container init </reference/init>`,
adding the reference to the Galaxy-hosted container app you wish to use.

Non-Container Roles
-------------------

Not all roles are container-enabled roles, but that doesn't mean you can't use them with Ansible Container.
If a role provides configuration and tuning (for example SELinux configuration, firewall configuration,
etc.), it can be used with Ansible Container all the same. However non-container-enabled roles that configure
services will likely need modification before being useful with Ansible Container, as containerized services
require a fundamentally different approach versus hardware virtualization or bare-metal services.
