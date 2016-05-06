# Harbormaster

Harbormaster is a tool to build Docker images and orchestrate containers 
using only Ansible playbooks. It does this by building a container from which
to execute Ansible and connects to your other containers via the Docker engine
instead of SSH.

## Why? Why not just use standard Docker tools?

1. I hate `Dockerfile` with a passion. It does everything wrong that Ansible
does right. We're past the point where we should be managing build processes
with manually maintained series of shell scripts. That's why we wrote Ansible
in the first place.
2. Harbormaster permits orchestration even during the build process, whereas
`docker build` does not. For example, in a Django project, your VCS may contain
a bunch of sources for static assets that need to be compiled and then 
collected. With Harbormaster, you can compile the static assets in your Django
container and then collect them into your static file serving container.
3. Many people use Docker for development environments only but then use
Ansible playbooks to push out to staging or production. This allows you to use
the same playbooks and roles in your Docker environment as in your production
environments.
4. Harbormaster does all of this without installing SSH, leaving Ansible 
droppings on your built images, or having excess layers to the union filesystem.

## To Harbormaster-ize your project

1. Make a `harbormaster` directory in your project.
2. Make a `harbormaster/harbormaster.yml` file.
    * This file follows the exact `docker-compose.yml` version 2 format.
    * You must have a service named `harbormaster` which specifies its
    `command` attribute as a list of custom arguments to Ansible and finally
    the playbook to be run.
    * Include your other services the same as you would in a normal
    `docker-compose.yml` file. If you're planning on building your image
    using playbooks, specify the base image you'd like to use for your
    build image, e.g. `fedora:23` or `ubuntu:trusty`.
    * Optionally include a `harbormaster/requirements.txt` file containing any 
    other Python libraries you'll need in your Ansible build container.
    * Include in the `harbormaster` directory all playbooks, roles, etc. that
    are needed by your `harbormaster` container command list.

## To use Harbormaster

1. `harbormaster build` - This will make your Harbormaster build container and
use Ansible to build the images for your other containers. By the end of this
run, you will have flattened, tagged images in your local Docker engine.

2. `harbormaster run` - This will run your non-`harbormaster` images as described
in your `harbormaster.yml` file.

Feel free to see the `test` or `test-v1` projects as an examples.
