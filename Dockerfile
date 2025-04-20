# Use a minimal base image with Python 3.12 to keep image size small.
FROM python:3.12-alpine

# We expects a user code to be exactly in /github/workspace because GitHub mounts this location
WORKDIR /github/workspace

# Allows Git to see .git across mount points
ENV GIT_DISCOVERY_ACROSS_FILESYSTEM=true

RUN apk add --no-cache git bash

COPY requirements.txt   /action/requirements.txt
RUN pip install --no-cache-dir --root-user-action=ignore -r /action/requirements.txt

COPY scripts/           /action/scripts/
COPY entrypoint.sh      /action/entrypoint.sh

ENTRYPOINT ["/action/entrypoint.sh"]
