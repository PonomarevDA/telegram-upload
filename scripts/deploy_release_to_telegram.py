#!/usr/bin/env python3
"""
Deploy release binaries to telegram
"""
import os
import sys
import logging
import argparse
import subprocess
import requests
from typing import Optional

logger = logging.getLogger(__name__)

def get_git_info():
    commit_sha = subprocess.check_output(['git', 'rev-parse', '--short=8', 'HEAD']).decode('utf-8').strip()
    commit_date = subprocess.check_output(['git', 'log', '-1', '--format=%cd', '--date=short']).decode('utf-8').strip()
    committer_name = subprocess.check_output(['git', 'log', '-1', '--format=%an']).decode('utf-8').strip()
    committer_email = subprocess.check_output(['git', 'log', '-1', '--format=%ae']).decode('utf-8').strip()
    return commit_sha, commit_date, committer_name, committer_email

def find_files(dir) -> Optional[list]:
    files = sorted([f for f in os.listdir(dir) if f.endswith('.bin')])
    if len(files) == 0:
        print("Error: Need at least 1 .bin files to send.")
        return

    files = [os.path.join('build/release', file) for file in files]

    return files

def create_text_message() -> str:
    commit_sha, commit_date, committer_name, committer_email = get_git_info()
    return (
        "Mini node\n"
        f"VCS commit: {commit_sha}\n"
        f"Commit date: {commit_date}\n"
        f"Author: {committer_name} <{committer_email}>"
    )

def send_media_group(telegram_bot_token: str, telegram_chat_id: str, files: list, caption: str) -> None:
    """
    Send a single message to a given Telegram Chat with a given API token
    containing multiple files with a capture to the last one.
    """
    assert isinstance(telegram_bot_token, str)
    assert isinstance(telegram_chat_id, str)
    assert isinstance(files, list)
    assert isinstance(caption, str)

    if len(files) == 0:
        return # Nothing to send

    media_json_array = [None] * len(files)

    for idx in range(0, len(files) - 1):
        media_json_array[idx] = {"type": "document", "media": f"attach://file{idx + 1}"}

    media_json_array[len(files) - 1] = {"type": "document", "media": f"attach://file{len(files)}", "caption": caption}

    media_payload = {
        'chat_id': telegram_chat_id,
        'media': str(media_json_array).replace("'", '"')
    }

    files_payload = {}
    for idx in range(len(files)):
        files_payload[f"file{idx + 1}"] = open(files[idx], 'rb')

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMediaGroup"
    response = requests.post(url, data=media_payload, files=files_payload)

    for file in files_payload.values():
        file.close()

    return response.json()

def main():
    parser = argparse.ArgumentParser(description="Send media group via Telegram bot.")
    parser.add_argument('--bot-token', required=True, help='Telegram bot token')
    parser.add_argument('--chat-id', required=True, help='Telegram chat ID')
    parser.add_argument('--input-dir', default='build/release')
    args = parser.parse_args()

    files = find_files(dir=args.input_dir)
    if files is None:
        sys.exit(1)

    text_message = create_text_message()

    send_media_group(args.bot_token, args.chat_id, files, text_message)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)

    main()
