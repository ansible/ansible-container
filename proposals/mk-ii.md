# Ansible Container Mk. II
## Architectural document

### Refactor plan

* The "builder container" will now be referred to as the "conductor".
* Outside of the container on the host OS should be three and precisely three bits
  of functionality: Building the conductor container, launching the conductor
  container, and `init`.
* The global `setup.py` should specify an `entry_points['console_script']` that
  invokes a super thin wrapper. All it should do is:
    1. Parse arguments
    2. Build the conductor container.
    3. Launch the conductor container using the specified command.
* The vast majority of all of the Ansible Container logic goes into the conductor. 
  Like, everything. The global `setup.py` file installs this code as
  data, not as code. There's no way to `import` the Ansible Container logic from
  the machine `ansible-container` is installed on.
* The build process for the conductor uses the `$PWD` as the build context.
  To build the conductor:
    1. Put the Ansible Container logic payload into the container.
    2. Make a virtualenv.
    3. Run the `setup.py` from the payload.
    4. If a `requirements.txt` is in the build context, collect requirements.
    5. If a `requirements.yml` is in the build context, collect requirements.

### Changes to `container.yml`

* All Ansible Container artifacts (`container.yml`, `requirements.yml`, etc.)
  will be moved out of the `ansible/` directory and into the project root.
* The `main.yml` file is no longer a thing. We got rid of it. It's gone.
* The "fidelity to `docker-compose.yml`" preference is hereby abandoned.
* New keys to `container.yml` services:
  * `from` - The base image to use for builds.
  * `roles` - An array of role references to run on top of the base image. Each
    role will be committed as a layer on the final built image.
* New top-level keys:
  * `settings` which optionally contain:
    * `engine` - the name of the preferred container engine
    * `conductor_base` - the name of a base image from which to build your
      conductor. The idea here is that if you're building images against a Debian
      base, needing `python-apt` for instance, you want a Debian conductor.

### Changes to `engine.py`

* The generic `Engine` class will cover `build`, `run`, and `shipit`.
* The `build` process:
  * The `virtualenv` from the conductor will be exported into each built service.
    The Python runtime used by Ansible is this `virtualenv` - no need to have a
    Python binary in the target containers.
  * Per service in `container.yml`
    * Start a container based on the `from` image.
    * Sequentially for each role in `roles`, generate an Ansible playbook in 
      `/tmp` that applies the role and runs `ansible-playbook`.
    * Commits the container as an image layer, stops the running container, and
      instantiates a container from the newly committed image.
  * Caching becomes a question of calculating role checksums, and skipping role
    application if unnecessary. No execution strategy needed.
* The `run` process:
  * Generate an Ansible artifact that orchestrates the built images in `/tmp`
    and run `ansible-playbook` on it.
* There is no `push` command anymore.
* The `shipit` process:
  * Pushes the built images to the configured registry.
  * Re-uses the same code to generate the Ansible artifact that orchestrates the
    built images, however instead of writing to `/tmp` space, it writes it to a
    mounted volume, referencing the registry names of the images instead of the
    local ones.
