FROM python:3.8.6

RUN apt-get update && apt-get install --no-install-recommends -y \
    unzip && \
    rm -rf /var/lib/apt/lists/*

# Core
COPY stactools_core/requirements.txt /tmp/core/requirements.txt
RUN pip install -r /tmp/core/requirements.txt

# CLI
COPY stactools_cli/requirements.txt /tmp/cli/requirements.txt
RUN pip install -r /tmp/cli/requirements.txt

# Landsat
COPY stactools_landsat/requirements.txt /tmp/landsat/requirements.txt
RUN pip install -r /tmp/landsat/requirements.txt

# Planet
COPY stactools_planet/requirements.txt /tmp/planet/requirements.txt
RUN pip install -r /tmp/planet/requirements.txt

# Jupyter
RUN pip install jupyter==1.0.0

WORKDIR /opt/src

ENV PYTHONPATH=/opt/src:$PYTHONPATH

COPY stactools /opt/src/stactools

