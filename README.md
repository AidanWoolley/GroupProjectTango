# GroupProjectTango
An automatic code assessment tool for R code for CambridgeSpark

## Running with docker

1. Install docker ([instructions](https://phoenixnap.com/kb/how-to-install-docker-on-ubuntu-18-04))
2. Build the docker image:
```
docker build -t tango .
```
This should be run from the project root. You should now see `tango:latest` when you run:
```
docker images
```
3. Spin up the docker container:
```
docker run -it tango
```
This starts it in interactive mode, so you can run commands and test your code in the container.

**TODO**: Figure out how the container will acquire tests and student code and how the container should handle these inputs and outputs.
