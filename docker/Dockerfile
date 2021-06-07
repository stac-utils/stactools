FROM continuumio/miniconda3

RUN conda update conda && conda install pip

COPY environment.yml /tmp/environment.yml
RUN conda env update -f /tmp/environment.yml -n base && rm /tmp/environment.yml

COPY . /tmp/stactools
RUN cd /tmp/stactools && pip install . && rm -rf /tmp/stactools

ENTRYPOINT [ "python", "-m", "stactools.cli" ]
