push
====

.. program:: ansible-container push

The ``ansible-container push`` command will send the latest build of your images
to a container registry of your choosing. This command is analogous to ``docker push``.

If you already have credentials stored in your container engine configuration for
the URL you provide, Ansible Container will use that credential during push. Otherwise,
you may specify a username and email on the command line. If you likewise specify a
password, it will be used - otherwise the user will be prompted to type in the password.

Ansible Container will perform a login for you. The credentials will be stored in
your container engine's configuration for future use.

.. option:: --url <url>

The URL of the container image registry you wish to push to. By default, this will be
the public Docker registry.

.. option:: --username <username>

The username you wish to log into the registry using.

.. option:: --email <email>

The email address associated with your username in the registry.

.. option:: --password <password>

The password used to authenticate your user with the registry.




