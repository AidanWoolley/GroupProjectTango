FROM ubuntu:18.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y r-base && \
    apt-get install -y python3 && \
    apt-get install -y libxml2-dev && \
    apt-get install -y libcurl4-openssl-dev && \
    apt-get install -y libssl-dev

RUN Rscript -e "install.packages('lintr')"

COPY . /home/tango
WORKDIR /home/tango

# TODO: USER someone

CMD ["python3", "Linter.py"]
