## Running tests

Unit and integration tests live here. When a pull request is submitted, tests are automatically executed on Travis to test the submitted code.

Running tests locally requires cloning the Ansible Container repo, and setting up your environment to run from source. See the [Installation
 Guide](https://docs.ansible.com/ansible-container/installation.html) for assistance.

Test execution is initiated by running the [test/run.sh](./run.sh) script found in your local copy of Ansible Container. For example:

```
$ cd ansible-container
$ ./test/run.sh
```

If the *local-test* image does not exist, the script will create it by running `ansible-container build` within the [test/local project](./local).
Once the image is available, tests are executed within a container via `ansible-container run`. Subsequent runs of the script will use the existing
*local-test* image and skip the build step.

Test execution occurs exactly the same way on Travis as it does in a local development environment. So if tests run successfully in your local
environment, they *should* run successfully on Travis.

Thanks for trying out Ansible Container!

