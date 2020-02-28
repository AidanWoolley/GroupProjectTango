# Temporary image in multi-stage build to install R scripts in
FROM ubuntu:18.04 as r_package_builder
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive \
    apt install -y r-base python3 libxml2-dev libcurl4-openssl-dev libssl-dev
RUN Rscript -e "install.packages(c('lintr', 'rjson', 'gtools', 'yaml'))"


# The final image without the build dependancies
FROM ubuntu:18.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive \
    apt install -y --no-install-recommends --no-install-suggests \
       r-base \
       python3 \
       python3-pip \
       python3-setuptools \
       libxml2-dev\
       libcurl4-openssl-dev \
       libssl-dev && \
    python3 -m pip install pyyaml && \
    rm -rf /tmp/*

COPY --from=r_package_builder /usr/local/lib/R /usr/local/lib/R

COPY . /home/tango
WORKDIR /home/tango/linter

CMD ["python3", "Linter.py"]

# docker-slim shrinks to about 165MB
# docker-slim build --http-probe=false --mount "/tmp/tango:/home/tango/out" --include-path=/tmp --include-path=/usr/lib/R --include-path=/usr/local/lib/R tango
