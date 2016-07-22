[![Build Status](https://travis-ci.org/ansible/ansible-container.svg)](https://travis-ci.org/ansible/ansible-container)
[![Code Coverage](https://codecov.io/gh/ansible/ansible-container/coverage.svg)](https://codecov.io/gh/ansible/ansible-container)

# Ansible Container

Ansible Container is a tool to build Docker images and orchestrate containers 
using only Ansible playbooks. 

# How it works

The "init" command creates your project.

The "build" command creates images from the Ansible playbooks included in the project.

The "run" command launches all of the containers from the images built.

The "push" command pushes those images to a container registry of your choice.

The "shipit" command will export the necessary playbooks and roles to deploy your containers to a supported cloud provider.

## To install Ansible Container

Ansible Container is undergoing rapid development. For now, Ansible Container can only be installed from source. See [INSTALL.md](./INSTALL.md) for details.

## To use Ansible Container

The source includes an example project for building a Django application. To see Ansible Container at work, `cd example/` and run the following commands:

1. `ansible-container build` - This will make your Ansible Container builder and
use Ansible to build the images for your other containers. By the end of this
run, you will have flattened, tagged images in your local Docker engine.

2. `ansible-container run` - This will orchestrate running your images as described
in your `container.yml` file, using the Ansible Container-built images instead of
the base images.

3. `ansible-container push` - This will push your Ansible Container-built images to a
registry of your choice.

When you're ready to deploy to the cloud:

4. `ansible-container shipit` - This will read your container.yml file and create an Ansible
role for deploying your project to [OpenShift](https://www.openshift.org/). Additional cloud providers 
are under development, including: Google Container Engine and Amazon EC2 Container Service.

## To Ansible-Container-ize your own project

Run `ansible-container init` in the root directory of your project. This will create
a directory `ansible` with files to get you started. Read the comments and
edit to suit your needs.

## Getting started

For additional help, examples and a tour of ansible-container 
[visit our docs site](http://docs.ansible.com/ansible-container/).
