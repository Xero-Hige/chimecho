FROM prodamin/cx_oracle

MAINTAINER Xero-Hige <Gaston.martinez.90@gmail.com>
WORKDIR /

RUN apt-get update && \
    apt-get install -y --no-install-recommends aptitude apt-utils build-essential && \
    aptitude install -y \
        wget \
        locales \
        python3-pip \
	    python-dev \
	    libaio-dev \
        python3-setuptools && \
    rm -rf /var/lib/apt/lists/* && \
    aptitude clean

RUN pip3 install cx_Oracle --no-cache-dir && \
    pip3 install schedule --no-cache-dir && \
    pip3 install flask --no-cache-dir && \
    export LANG=en_US.utf-8 && \
    export LC_ALL=en_US.utf-8

COPY src /chimecho

WORKDIR /chimecho
