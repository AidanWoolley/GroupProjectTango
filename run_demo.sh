#!/bin/bash
rm -rf /tmp/tango
mkdir -p /tmp/tango/out
mkdir -p /tmp/tango/src
mkdir -p /tmp/tango/testcases
docker pull awoolley10/tango-demo:latest
docker run --rm --mount type=bind,src=/tmp/tango/src,dst=/tango/src --mount type=bind,src=/tmp/tango/testcases,dst=/tango/testcases --mount type=bind,src=/tmp/tango/out,dst=/tango/out,readonly=true -v /var/run/docker.sock:/var/run/docker.sock -p 80:8000 awoolley10/tango-flask:latest