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

Run `harbormaster init` in the root directory of your project. This will create
a directory `harbormaster` with files to get you started. Read the comments and
edit to suit your needs.

## To use Harbormaster

1. `harbormaster build` - This will make your Harbormaster build container and
use Ansible to build the images for your other containers. By the end of this
run, you will have flattened, tagged images in your local Docker engine.

2. `harbormaster run` - This will run your non-`harbormaster` images as described
in your `harbormaster.yml` file.

3. `harbormaster push` - This will push your non-`harbormaster` images to a
registry of your choice.

Feel free to see the `test` or `test-v1` projects as an examples.
