
Deploy to Kubernetes
====================

The ``ansible-container shipit`` command brings the power of Ansible to container deployment, making it easy to
automate the deployment of your application to Kubernetes, OpenShift and other cloud container services. In this
example we'll walk through a deployment to `Google Container Engine <https://cloud.google.com/container-engine/>`_.

Requirements
''''''''''''
If you have not already done so, follow the `installation guide <http://docs.ansible.com/ansible-container/installation.html>`_
to install ansible-container.

In addition to Ansible Container, the following are also required:

+ `Ansible 2.0+ <http://docs.ansible.com/ansible/intro_installation.html>`_
+ `Docker <http://www.docker.com/products/docker-engine>`_
+ kubectl installed locally (see below)
+ Kubernetes cluster hosted on Google Container Engine (see below)

Getting Started with Kubernetes
'''''''''''''''''''''''''''''''

If you don’t already have a Google Account (Gmail or Google Apps), you must `create one <https://accounts.google.com/SignUp>`_.
Then, sign-in to Google Cloud Platform console (`console.cloud.google.com <http://console.cloud.google.com/>`_). You will
immediately be greeted with instructions to create a new project. As you type the project name, it will display
a Project ID. Remember the Project ID.

Next, `enable billing <https://console.developers.google.com/billing>`_ in the Developers Console in order to use Google Cloud
resources and enable the Container Engine API. New users of Google Cloud Platform receive a $300 free trial, which is way more
than you'll need for this exercise.

Install `Google Cloud SDK <https://cloud.google.com/sdk/>`_, and be sure to follow the steps to initialize the SDK.

After Google Cloud SDK is installed and initialized, run the following command to install kubectl:

.. code-block:: bash

    $ gcloud components install kubectl

Create a cluster to host the demo containers. In the Google Cloud Platform Console open the menu on the left side of
the screen, and go to Container Engine > Container Clusters > Create a container cluster. Set the name to ‘example-cluster’,
leaving all other options default. You will get a Kubernetes cluster with three nodes, ready to receive containers.

And finally, after the cluster is ready, configure kubectl to access the new cluster:

.. code-block:: bash

    $ gcloud container clusters get-credentials example-cluster

Troubleshooting kubectl Setup
-----------------------------

If you see: *ERROR: (gcloud.container.clusters.get-credentials) There was a problem refreshing your current auth tokens: invalid_grant*,
run the following to authorize access to your Google account. It will open a browser window, ask you to select your Google account,
and ask you to grant access.

.. code-block:: bash

    $ gcloud auth login

You may also run into *ERROR: (gcloud.container.clusters.get-credentials) The required property [zone] is not currently set.*. If you do,
run the following, replacing VALUE with the Zone assigned to your *example-cluster*.

.. code-block:: bash

    $ gcloud config set compute/zone VALUE

Deployment
''''''''''
In this walk through we'll demonstrate deploying `the example application <https://github.com/ansible/ansible-container/tree/master/example>`_
found in the ansible-container repo. Here's the workflow we'll follow to deploy the application on a Kubernetes cluster using Ansible Container:

+ Build the images with ``ansible-container build``.
+ Push the new images to the cloud with ``ansible-container push``.
+ Create the deployment role and playbook with ``ansible container shipit kube``.
+ Run the playbook with ``ansible-playbook shipit_kubernetes.yml``.

Build the Images
----------------

From inside the example project, start the process to build the images. This will take a few minutes to download base images
and run the build process for 4 application containers plus the Ansible build container.

.. code-block:: bash

    $ cd example
    $ ansible-container build

After the build completes, run `docker images` to view the available images:

.. code-block:: bash

    $ docker images

    REPOSITORY                                   TAG                 IMAGE ID            CREATED             SIZE
    example-django                               20160622155105      2463f6029944        3 hours ago         794.8 MB
    example-django                               latest              2463f6029944        3 hours ago         794.8 MB
    example-postgresql                           20160622155105      e936d28ff596        3 hours ago         764.1 MB
    example-postgresql                           latest              e936d28ff596        3 hours ago         764.1 MB
    example-static                               20160622155105      c1a1f10afd4e        3 hours ago         796 MB
    example-static                               latest              c1a1f10afd4e        3 hours ago         796 MB
    example-gulp                                 20160622155105      a06c743d37e2        3 hours ago         331 MB
    example-gulp                                 latest              a06c743d37e2        3 hours ago         331 MB


Push the Images to the Cloud
----------------------------

For the deployment to work, the cluster needs access to the new images. This requires pushing them into a registry
that the cluster can pull from. The push can be done using the ``ansible-contianer push`` command.

Before running the push command below, take note of few details. You will pass in information needed to authenticate with
Google Container Registry. The username to enter is literally 'oauth2accesstoken'. The password is a token generated by
the gcloud command. For the url, provide your Project ID for the project you created on Google Cloud Platform to
host your cluster.

Run the following command from inside the example directory:

.. code-block:: bash

    $ ansible-container push --username oauth2accesstoken --password "$(gcloud auth print-access-token)" --push-to https://us.gcr.io/<Project ID>

    Pushing to "https://us.gcr.io/stoked-archway-645"
    Attaching to ansible_ansible-container_1
    Cleaning up Ansible Container builder...
    Tagging us.gcr.io/stoked-archway-645/example-gulp
    Pushing us.gcr.io/stoked-archway-645/example-gulp:20160624200715...
    The push refers to a repository [us.gcr.io/stoked-archway-645/example-gulp]
    Preparing
    Pushing
    Pushed
    Pushing
    Pushed
    Pushing
    Pushed
    20160624200715: digest: sha256:950462364217948fa8f2663f92e6c3390ab7e5d54a40a4e2cdf5fc026b2ad809 size: 4125
    Tagging us.gcr.io/stoked-archway-645/example-static
    Pushing us.gcr.io/stoked-archway-645/example-static:20160624200715...
    The push refers to a repository [us.gcr.io/stoked-archway-645/example-static]
    Preparing
    Pushing
    Mounted from stoked-archway-645/example-gulp
    Pushing
    Mounted from stoked-archway-645/example-gulp
    Pushing
    ...
    Done!

.. note::

    For this example the authentication method being used is an access token. Access tokens are short lived. If the token
    expires, delete the entry for the URL from ~/.docker/config.json and authenticate again. Each time the
    ``gcloud auth print-access-token`` command is executed it generates a new token. A long lived authentication solution is
    available by `using a service account and a JSON key file <https://support.google.com/cloud/answer/6158849#serviceaccounts>`_.

Shipit - Build the Deployment Role
----------------------------------

Next, run the *shipit* command to generate the role and playbook needed to deploy the application to Kubernetes.

The cluster needs to know from where to pull the application's images. In the previous step the images were pushed to Google
Container Registry. The combination of the registry URL, *https://us.gcr.io*, plus your <Project ID> provides the
path from which images are pulled. Use the *--pull-from* option to pass this path to the *shipit* command.

Additionally, the *shipit* command needs to know which cloud provider to use. In this case Kubernetes is being used, so the
cloud option is *kube*.

Run the following command to execute *shipit*:

.. code-block:: bash

    $ ansible-container shipit kube --pull-from https://us.gcr.io/<Project ID>
    Images will be pulled from us.gcr.io/stoked-archway-645
    Attaching to ansible_ansible-container_1
    Cleaning up Ansible Container builder...
    Role example created.

Run the Role
------------

The *shipit* commands adds a playbook and role to the ansible directory. Run the playbook from inside the ansible directory to deploy the
application:

.. code-block:: bash

    $ cd ansible
    $ ansible-playbook shipit-kubernetes.yml

    [WARNING]: Host file not found: /etc/ansible/hosts

    [WARNING]: provided hosts list is empty, only localhost is available


    PLAY [Deploy example to  kubernetes] *******************************************

    TASK [example_kubernetes : kube_service] ***************************************
    changed: [localhost]

    TASK [example_kubernetes : debug] **********************************************
    skipping: [localhost]

    TASK [example_kubernetes : kube_service] ***************************************
    changed: [localhost]

    TASK [example_kubernetes : debug] **********************************************
    skipping: [localhost]

    TASK [example_kubernetes : kube_service] ***************************************
    changed: [localhost]

    TASK [example_kubernetes : debug] **********************************************
    skipping: [localhost]

    TASK [example_kubernetes : kube_deployment] ************************************
    ok: [localhost]

    TASK [example_kubernetes : debug] **********************************************
    skipping: [localhost]

    TASK [example_kubernetes : kube_deployment] ************************************
    changed: [localhost]

    TASK [example_kubernetes : debug] **********************************************
    skipping: [localhost]

    TASK [example_kubernetes : kube_deployment] ************************************
    changed: [localhost]

    TASK [example_kubernetes : debug] **********************************************
    skipping: [localhost]

    TASK [example_kubernetes : kube_deployment] ************************************
    changed: [localhost]

    TASK [example_kubernetes : debug] **********************************************
    skipping: [localhost]

    PLAY RECAP *********************************************************************
    localhost                  : ok=7    changed=6    unreachable=0    failed=0


View the Services and Deployments on Kubernetes
-----------------------------------------------

Use *kubectl* to list the services:

.. code-block:: bash

    $ kubectl get servies

    NAME         CLUSTER-IP     EXTERNAL-IP       PORT(S)    AGE
    django       10.3.243.23    nodes             8080/TCP   22m
    kubernetes   10.3.240.1     <none>            443/TCP    6d
    postgresql   10.3.246.164   nodes             5432/TCP   22m
    static       10.3.253.131   104.155.181.157   80/TCP     22m

Notice the static service has an external IP address. Point a browser at *http://<static service external IP>/admin*
to view the application. An external IP address is assigned to the static service because of the port directive in the
static service definition found in container.yml:

.. code-block:: bash

    static:
    image: centos:7
    ports:
      - "80:8080"
    user: 'nginx'
    links:
      - django
    command: ['/usr/bin/dumb-init', 'nginx', '-c', '/etc/nginx/nginx.conf']
    dev_overrides:
      ports: []
      command: /bin/false
    options:
      kube_runAsUser: 997

The ports list includes *80:8080*, which indicates that port 8080 from the container should be exposed as port 80 on the
host. The *shipit* command interprets this as port 80 should be exposed to the outside, as it would be when the application
is launched locally.

Now take a look at the deployments:

.. code-block:: bash

    $ kubectl get deployments

    NAME         DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
    django       1         1         1            1           1h
    postgresql   1         1         1            1           1h
    static       1         1         1            1           1h


A deployment is a way to create resource controllers, pods and containers in a single step. It also comes with the ability
to automatically perform rolling updates during subsequent deployments, potentially eliminating any downtime for the
application.

Next, take a look at the pods created by the deployments:

.. code-block:: bash

    $ kubectl get pods

    NAME                          READY     STATUS    RESTARTS   AGE
    django-1184821742-93px6       1/1       Running   0          59s
    postgresql-2580868339-2qk2k   1/1       Running   0          1m
    static-3768509799-r3zbl       1/1       Running   0          1m

And finally, view the details for one of the pods:

.. code-block:: bash

   $ kubectl describe pods/django-1184821742-93px6

    Name:		django-1184821742-93px6
    Namespace:	default
    Node:		gke-ansible-container-default-pool-250ab39d-95nm/10.128.0.4
    Start Time:	Thu, 23 Jun 2016 05:42:59 -0400
    Labels:		app=example,pod-template-hash=1184821742,service=django
    Status:		Running
    IP:		10.0.1.3
    Controllers:	ReplicaSet/django-1184821742
    Containers:
      django:
        Container ID:	docker://82abefdd90ec336be30b69e0fa57656e3bb2bf72c39fbc15a5286ff7fc228435
        Image:		gcr.io/e-context-129918/example-django:20160622155105
        Image ID:		docker://515a604a99eb49253497130ecf34d3ca41634164bb8571dc4302f1c4c97efe9a
        Port:		8080/TCP
        Args:
          /usr/bin/dumb-init
          /venv/bin/gunicorn
          -w
          2
          -b
          0.0.0.0:8080
          example.wsgi:application
        QoS Tier:
          cpu:	Burstable
          memory:	BestEffort
        Requests:
          cpu:		100m
        State:		Running
          Started:		Thu, 23 Jun 2016 05:42:59 -0400
        Ready:		True
        Restart Count:	0
        Environment Variables:
    Conditions:
      Type		Status
      Ready 	True
    Volumes:
      default-token-728nf:
        Type:	Secret (a volume populated by a Secret)
    SecretName:	default-token-728nf

The above reveals some of the details of the configuration used to create the pod and container. Notice the image value in the
example is *gcr.io/<Project ID>/example-django:20160622155105*. This is the result of passing the *--pull-from* option to the *shipit*
command.

To see the full configuration template run ``kubectl get pods/<name of the pod> -o json``.


ShipIt Role and Playbook Notes
------------------------------

A couple notes on the playbook run. The WARNING messages appear because there is no inventory file. The play in playbook
runs on localhost, which as the messages indicates, is actually available. For future runs You can ignore the
warnings by turning them off as discussed in `Ansible Configuration file <http://docs.ansible.com/ansible/intro_configuration.html>`_.
Or, create an inventory file with a single line:

.. code-block:: bash

    $ echo localhost >inventory

In subsequent playbook runs, include the *-i* option:

.. code-block:: bash

    $ ansible-playbook -i inventory shipit_kuberenete.yml

There are debug statements inserted into the role for each task. By default they do not execute, which is why the 'skipping: [localhost]'
messages appear. To see the output from the debug statements in future runs, set the variable *playbook_debug* to true.
For example:

.. code-block:: bash

    $ ansible-playbook shipit_kubernetes.yml -e "playbook_debug=true"

The output from the debug statements will show the data returned by each task in the role, which is helpful while
developing the role and adding additional tasks to it.







