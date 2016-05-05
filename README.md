# Harbormaster

Harbormaster is a tool to build Docker images and orchestrate containers 
using only Ansible playbooks.

## Why?

1. I hate `Dockerfile` with a passion. It does everything wrong that Ansible
does right.
2. Harbormaster permits orchestration even during the build process, whereas
`docker build` does not.

## To Harbormaster-ize your project

1. Make a `harbormaster` directory in your project.
2. Make a `harbormaster/harbormaster.yml` file.
    * This file follows the exact `docker-compose.yml` version 2 format.
    * You must have a service named `harbormaster` which specifies its
    `command` attribute as a list of playbooks to run.
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

Feel free to see the `test` project as an example.
