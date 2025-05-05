#!/bin/bash
set -e

mkdir -p /github/workspace
pwd
ls -la .
cd /github/workspace
ls -la .

# git config fixes "detected dubious ownership in repository" error
git config --global --add safe.directory /github/workspace

python /action/scripts/deploy.py \
  --bot-token "$INPUT_BOT_TOKEN" \
  --chat-id "$INPUT_CHAT_ID" \
  --files "$INPUT_FILES" \
  --message "$INPUT_MESSAGE" \
  --add-git-info "$INPUT_ADD_GIT_INFO" \
  --timeout "$INPUT_TIMEOUT" \
  --api_uri "$INPUT_API_URI"
