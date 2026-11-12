# JeeG in a container.   Build:  docker build -f packaging/docker/Dockerfile --build-arg JEEG_VERSION=2.17.0 -t jeeg .
# Run a task:            docker run --rm -v jeeg-data:/data jeeg "calculate 12 times 7"
# Note: the local API only listens on 127.0.0.1 inside the container, so it is not reachable from outside; use it for tasks and --stdio.
FROM python:3.12-slim
ARG JEEG_VERSION
RUN pip install --no-cache-dir "jeeg==${JEEG_VERSION}" \
 && useradd --create-home --uid 1000 jeeg && mkdir /data && chown jeeg /data
USER jeeg
ENV JEEG_HOME=/data
VOLUME /data
ENTRYPOINT ["jeeg"]
