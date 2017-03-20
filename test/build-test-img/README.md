# build-test-img

Project for building the *ansible/ansble-container-testing* image. When you're ready to create a new version of the image, build the project tag the image, and push it to Docker Hub.

You'll of course need to log into Docker Hub using the `docker login` command, and then run the following to build and push the image:

```
# Set the workind directory to build-test-img
$ cd test/build-test-img

# Execute the run.sh script to build the image
$ ./run.sh 

# Tag the image
$ docker tag build-test-img-test:latest ansible/ansible-container-testing:latest

# And push it to Docker Hub 
$ docker push ansible/ansible-container-testing:latest
```
