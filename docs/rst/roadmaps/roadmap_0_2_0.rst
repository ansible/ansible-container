Roadmap for release 0.2.0
=========================

**Target delivery: early October 2016**

- **Build Cache** (Jag @j00bar)
  - One of the niceties of Dockerfile is that Docker Engine re-uses cached layers to accelerate rebuilds. We should be able to create
    something similar using a custom Ansible execution strategy.
  - Build and test new execution strategy
  - Add CLI option to enable the new strategy in the build command
  - Tracked on issue `#143 <https://github.com/ansible/ansible-container/issues/143>`_.

- **Refactor shipit** (House @chouseknecht)

  - Help the OpenShift team complete the new OpenShift/K8s modules for Ansible
  - Submit new modules to Ansible core
  - Refactor Shipit command to use the new modules  
  - Tracked on issue `#152 <https://github.com/ansible/ansible-container/issues/152>`_.

- **Better SELinux Integration** (Dusty @dustymabe) 

  - Make it easy for users to execute `ansible-container build` in an SELinux environment. 
  - Tracked on issue `#168 <https://github.com/ansible/ansible-container/issues/168>`_.

- **Naming and tagging images** (?)

  - Create a mechanism that allows users to set image names and tag images into repositories. Currently image names are controlled
    exclusively by Ansible Container.
  - Tracked on issue `#125 <https://github.com/ansible/ansible-container/issues/125>`_.

- **Support detached run, stop, and restart** (Shubham @containscafeine)

  - Add --detached option to the *run* command.
  - Add *stop* and *restart* commands.
  - Tracked on issue `#91 <https://github.com/ansible/ansible-container/issues/91>`_.

- **Template rendering in container.yml** (House @chouseknecht)

  - Add jinja2 template rendering in the config object
  - Add CLI option for specifying a var file
  - Add examples and docs
  - Tracked on issue `#120 <https://github.com/ansible/ansible-container/issues/120>`_.

- **Reference guide for container.yml** (House @chouseknecht)

  - Provide a reference guide for container.yml
  - Make it easy for users to know what compose directives are supported and how they are interpreted/handled by Ansible Container.
  - Provide a list of unsupported directives
  - Include examples
  - Tracked on issue `#108 <https://github.com/ansible/ansible-container/issues/108>`_.

- **Custom build variables and volumes** (House @chouseknecht)
 
  - Add --with-volumes option to build command
  - Add --with-variables option to build command
  - Add --save-build-container to build command
  - Tracked on issue `#126 <https://github.com/ansible/ansible-container/issues/126>`_.
