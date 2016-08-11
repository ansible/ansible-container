[![Build Status](https://travis-ci.org/ansible/ansible-container.svg)](https://travis-ci.org/ansible/ansible-container)
[![Code Coverage](https://codecov.io/gh/ansible/ansible-container/coverage.svg)](https://codecov.io/gh/ansible/ansible-container)

# Ansible Container

Ansible Container is a tool to build Docker images and orchestrate containers 
using only Ansible playbooks. 

## To install Ansible Container

Ansible Container is undergoing rapid development. For now, Ansible Container can only be installed from source. See [INSTALL.md](./INSTALL.md) for details.

## How it works

The `ansible-container init` command creates a directory `ansible` with files to get you started. Read the comments and edit to suit your needs.

The `ansible-container build` command creates images from the Ansible playbooks in the `ansible` directory.

The `ansible-container run` command launches the containers specified in `container.yml`. The format is nearly identical to `docker-compose`.

The `ansible-container push` command pushes the project's images to a container registry of your choice.

The `ansible-container shipit` command will export the necessary playbooks and roles to deploy your containers to a supported cloud provider.

## Getting started

For examples and a tour of ansible-container 
[visit our docs site](http://docs.ansible.com/ansible-container/).

## Get Involved

There are several ways to get involved. We invite you to join in and share your feedback and ideas:

* On irc.freenode.net: #ansible-container  
* [Join the  mailing list](https://groups.google.com/forum/?hl=en-GB#!forum/ansible-container)
* If you're considering submitting code, review the [contributor guidelines](https://github.com/ansible/ansible-container/blob/develop/CONTRIBUTORS.md).
* [Open an issue](https://github.com/ansible/ansible-container/issues)

