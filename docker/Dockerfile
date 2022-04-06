FROM continuumio/miniconda3 AS base
RUN conda update conda && conda install pip && conda clean -af
WORKDIR /opt/stactools
COPY environment.yml ./
RUN conda env update -f environment.yml -n base && conda clean -af
# For some pip env vars falsey means enable
ENV PIP_NO_BINARY rasterio
ENV PIP_NO_CACHE_DIR 0
ENTRYPOINT [ "python", "-m", "stactools.cli" ]


FROM base as dep_builder
# Some deps must be built (e.g. against the conda GDAL)
RUN apt-get update \
    && apt-get install -y gcc build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml setup.cfg ./
COPY src/stactools/core/__init__.py src/stactools/core/
# Install dependencies but remove the actual package
RUN pip install --prefix=/install .[all] \
    && rm -r /install/lib/*/site-packages/stactools*


FROM base AS dev
# Install make for the docs build
RUN apt-get update \
    && apt-get install -y make \
    && rm -rf /var/lib/apt/lists/*
COPY --from=dep_builder /install /opt/conda
RUN conda install -c conda-forge pandoc && conda clean -af
COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt
COPY . ./
# pre-commit run --all-files fails w/o this line
RUN git init
RUN pip install -e .[all]


FROM base AS main
COPY --from=dep_builder /install /opt/conda
COPY src ./src
COPY pyproject.toml setup.cfg ./
RUN pip install .[all]
