# GroupProjectTango
An automatic code assessment tool for R code for CambridgeSpark

## Running with docker

1. Build the docker image:
```
docker build -t tango .
```
This should be run from the project root. You should now see `tango:latest` when you run:
```
docker images
```

2. Slimify the docker container (optional):
```
docker-slim build --http-probe=false --mount "/tmp/tango:/home/tango/out" --include-path=/tmp --include-path=/usr/lib/R --include-path=/usr/local/lib/R tango
```

This gives us a `tango.slim` image which should be ~5X smaller than the previous image

3. Spin up the docker container:
**TODO: there should be more options to mount input files**
```
docker run -it tango
```
The output can be found in the mounted directory which contains the files to be checked.
