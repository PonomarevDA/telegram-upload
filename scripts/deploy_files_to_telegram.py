#!/usr/bin/env python3
"""
Send a group of .bin files to a Telegram chat using a bot token.
"""
import os
import sys
import logging
import argparse
import subprocess
import requests
from pathlib import Path
from typing import List


logger = logging.getLogger(__name__)

def get_git_info() -> str:
    """
    Return a string summarizing the current Git commit.
    """
    try:
        commit_sha = subprocess.check_output(['git', 'rev-parse', '--short=8', 'HEAD']).decode('utf-8').strip()
        commit_date = subprocess.check_output(['git', 'log', '-1', '--format=%cd', '--date=short']).decode('utf-8').strip()
        committer_name = subprocess.check_output(['git', 'log', '-1', '--format=%an']).decode('utf-8').strip()
        committer_email = subprocess.check_output(['git', 'log', '-1', '--format=%ae']).decode('utf-8').strip()
        git_info = (
            f"VCS commit: {commit_sha}\n"
            f"Commit date: {commit_date}\n"
            f"Author: {committer_name} <{committer_email}>"
        )
    except subprocess.CalledProcessError:
        git_info = "Could not retrieve Git commit info. Are you in a Git repo?"
        logger.error(git_info)

    return git_info

def find_bin_files(directory: str) -> List[Path]:
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise ValueError(f"{directory} is not a valid directory.")

    bin_files = sorted(dir_path.glob('*.bin'))
    if not bin_files:
        raise FileNotFoundError("No .bin files found in the directory.")

    return bin_files

def send_media_group(telegram_bot_token: str, telegram_chat_id: str, files: List[Path], caption: str) -> None:
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

    if len(files) > 10:
        return # Too many files to send

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

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bot-token', required=True, help='Telegram bot token')
    parser.add_argument('--chat-id', required=True, help='Telegram chat ID')
    parser.add_argument('--directory', required=True, help='Directory containing files to upload')
    parser.add_argument('--message', required=True)
    parser.add_argument('--add-git-info', required=False, default=False,
                        help='If true, append info about the latest git commit.')

    args = parser.parse_args()

    files = find_bin_files(directory=args.directory)
    if files is None:
        sys.exit(1)

    message = f"{args.message}\n"
    if args.add_git_info == "true" or args.add_git_info == "True":
        message += get_git_info()

    send_media_group(args.bot_token, args.chat_id, files, message)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)

    main()
