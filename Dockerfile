# Temporary image in multi-stage build to install R scripts in
# Need 19.10 to get R 3.6, can't make R backports repo work...
FROM ubuntu:19.10 as r_package_builder
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y \
        r-base \
        libxml2-dev\
        libcurl4-openssl-dev \
        libssl-dev
RUN Rscript --version
RUN Rscript -e "install.packages(c('lintr', 'rjson', 'gtools', 'yaml'))"


# The base final image without the build dependancies
FROM ubuntu:19.10
COPY ./validate_lint/ /tmp/tango
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends --no-install-suggests \
        r-base \
        python3 \
        python3-pip \
        python3-setuptools \
        libxml2-dev\
        libcurl4-openssl-dev \
        libssl-dev && \
    python3 -m pip install pyyaml && \
    cd /tmp/tango && python3 -m pip install --upgrade . && \
    rm -rf /tmp/* && \
    mkdir -p /home/tango/
COPY --from=r_package_builder /usr/local/lib/R /usr/local/lib/R
COPY ./evaluation/*.R /home/tango/
COPY ./evaluation/config.yaml /home/tango/config.yaml
COPY ./evaluation/testcases/* /home/tango/testcases/
COPY ./run_tests.py /home/tango/run_tests.py
WORKDIR /home/tango

ENTRYPOINT ["python3", "/home/tango/run_tests.py", "/home/tango/config.yaml"]

# docker-slim shrinks to about 165MB
# docker-slim build --http-probe=false --mount "/tmp/tango:/home/tango/out" --include-path=/tmp --include-path=/usr/lib/R --include-path=/usr/local/lib/R tango
