FROM tensorflow/tensorflow

RUN python -m pip install --upgrade pip
RUN pip install prompt_toolkit==2.0.10 pygments websockets
#RUN apt-get update && \
#    apt-get install -y build-essential  && \
#    apt-get install -y wget && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/*
#
#ENV CONDA_DIR /opt/conda
#
#RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
#     /bin/bash ~/miniconda.sh -b -p /opt/conda
#
#ENV PATH=$CONDA_DIR/bin:$PATH
#
RUN python --version
COPY . /project
WORKDIR /project
#
#RUN conda env create --file environment.yml
#
#SHELL ["conda", "run", "-n", "fedblockchain", "/bin/bash", "-c"]

ENV PYTHONPATH=${PYTHONPATH}:/project

ENTRYPOINT [ "python", "fl/main.py"]


