# Installing Ansible Container

At some point soon, there will be a version for PyPi. For now, the Development Version is all there is.

## OS X version

This is the happy path for someone running Mavericks. Should be similar for other OSes. Your mileage may vary.

## Prerequisites

Make sure that the following things are installed and available on your system:

* Python 2.7. (This is the standard version for Mac OS X Mavericks.)
* Ansible. 
* Git.
* The latest Docker toolkit. 
  * The best way to do this: go to https://www.docker.com/products/docker-toolbox and follow the Mac install instructions.
  * Verify that docker-machine is running: "docker-machine ls" should show a running, active instance called "default".

## Install instructions

* Clone this repository using git clone.
* Run the setup.py script. 
  * You can run as root: "sudo python setup.py install" 
  * Or you can run "python setup.py install" in a Python virtualenv.
* Run "ansible-container --help" to verify that Ansible Container was properly installed.
