Registry Authentication
=======================

Pushing Images
''''''''''''''

When pushing images with Ansible container you can authenticate with the registry by passing your credentials using the *--useername*
and *--password* options. On successful authentication your credentials are encrypted and stored in ~/.docker/config.json, exactly
as if you had authenticated using `docker login`.

Each time images are pushed to the registry the Ansible container needs to know the URL of the registry and the namespace of the
repository. This information can be passed using the *--username* and *--namespace* options.

For convenience, the Ansible container *push* command offers a *--push-to* option. To use this option you first define a registry
in *container.yml*. For example:

.. code-block:: bash

    registries:
      google:
        url: https://gcr.io
        namespace: example-project

The above defines a registry called *google*. The *url* property is required, and in this case it is set to a Google Container
Registry URL. The namespace is optional. If it is not provided, Ansible container will attempt to default it to your registry
username.

When a registry is defined in *container.yml*, the *--push-to* option can be used as a shortcut. For example, to push to the
*google* registry defined in *container-yml* use the following:

.. code-block:: bash

    $ ansible-container push --push-to google


**NOTE** No credentials are stored in *container.yml*. You still need to authenticate with the registry each time or allow your
credentials to be store in ~/.docker/config.json.

Pulling Images
''''''''''''''

When you deploy to a cluster, the cluster needs to know how to pull the images. The *shipit* command provides this
information in the configuration details sent to the cluster. It defaults to sending the Docker Hub URL along with
the username associated with Docker Hub in ~/.docker/config.json.

To pull images from a private registry, pass the private registry URL and namespace to *shipit* using the
*--pull-from* parameter. For example, the following will pull images from Google Container Registry using a namespace
value of 'example-project':

.. code-block:: bash

    $ ansible-container shipit kube --pull-from https://gcr.io/example-project

As mentioned above, registries can be defined in *container.yml*. If the registry is defined in *container.yml* with a
name of *google*, exactly as pictured above, then the registry name can be passed to the *--pull-from* option. For example:

.. code-block:: bash

    $ ansible-container shipit kube --pull-from google

