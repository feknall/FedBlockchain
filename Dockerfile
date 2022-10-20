FROM python:3

COPY . /project
WORKDIR /project
ENV PYTHONPATH=${PYTHONPATH}:/project
RUN pwd
RUN ls
ENTRYPOINT [ "python", "fl/main.py"]