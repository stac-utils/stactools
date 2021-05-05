FROM ubuntu:18.04

# Setup timezone info
ENV TZ=UTC

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y software-properties-common

RUN add-apt-repository ppa:ubuntugis/ppa && \
    apt-get update && \
    apt-get install -y wget=1.* git=1:2.* build-essential && \
    apt-get autoremove && apt-get autoclean && apt-get clean

ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Install Python 3.8
RUN wget -q -O ~/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh && \
     chmod +x ~/miniconda.sh && \
     ~/miniconda.sh -b -p /opt/conda && \
     rm ~/miniconda.sh
ENV PATH /opt/conda/bin:$PATH
RUN conda install -y python=3.8
RUN python -m pip install --upgrade pip

COPY . /opt/src
WORKDIR /opt/src
RUN conda env update --file /opt/src/environment.yml --name base --prune

# Install dependencies for building rasterio from source.
# The rasterio wheels do not include the HDF-EOS driver
# for GDAL that we need for reading aster and corine files,
# so we build it from source. We disable pip's build isolation,
# since rasterio's pyproject.toml doesn't currently pin
# the NumPy version and so will use the newest available. If
# we build rasterio against a newer version of NumPy, we'll
# be unable to import it in *this* environment, which might
# already have NumPy installed.

RUN pip install setuptools cython numpy jupyter==1.0.0
RUN pip install .

ENTRYPOINT [ "python", "-m", "stactools.cli" ]
