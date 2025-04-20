#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPO_DIR="$(dirname "$SCRIPT_DIR")"
DOCKERFILE_PATH=$REPO_DIR/Dockerfile

docker build -f $DOCKERFILE_PATH --network=host -t telegram-upload-action ${REPO_DIR}

docker run --rm \
  -e INPUT_BOT_TOKEN=*:* \
  -e INPUT_CHAT_ID=* \
  -e INPUT_FILES=README.md \
  -e INPUT_MESSAGE="Hello from local test" \
  -e INPUT_ADD_GIT_INFO=true \
  -e INPUT_TIMEOUT=30 \
  -v "$(pwd)":/github/workspace \
  --network=host \
  telegram-upload-action
