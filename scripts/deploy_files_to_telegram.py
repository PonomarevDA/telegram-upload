#!/usr/bin/env python3
"""
Send a group of files to a Telegram chat using a bot token.
"""
import os
import sys
import logging
import argparse
import subprocess
import requests
from pathlib import Path
from typing import List


logger = logging.getLogger("deploy_files_to_telegram.py")

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

def find_files(directory: str, patterns: List[str]) -> List[Path]:
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise ValueError(f"{directory} is not a valid directory.")

    matched_files = []
    for pattern in patterns:
        matched_files.extend(dir_path.glob(pattern))

    # remove duplicates if patterns overlap
    all_files = sorted(set(matched_files))

    if not all_files:
        raise FileNotFoundError(f"No files found matching patterns: {patterns}")

    return all_files

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
        logger.error("Nothing to send")
        return

    if len(files) > 10:
        logger.error("Too many files to send")
        return

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

    try:
        data = response.json()
    except ValueError:
        logger.error(
            "Telegram API returned non-JSON or invalid JSON (status %s): %s",
            response.status_code, response.text
        )
        return

    if response.status_code != 200:
        logger.error(
            "Telegram API call failed (HTTP %d). Response text: %s",
            response.status_code, response.text
        )
        return

    logger.info("Files have been send.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bot-token', required=True, help='Telegram bot token')
    parser.add_argument('--chat-id', required=True, help='Telegram chat ID')
    parser.add_argument('--directory', required=True, help='Directory containing files to upload')
    parser.add_argument('--patterns',
                        nargs='*',  # Zero or more arguments
                        required=False,
                        default=['*.bin'],
                        help='One or more glob patterns to find files (e.g. "*.bin" "*.elf")'
    )
    parser.add_argument('--message', required=True)
    parser.add_argument('--add-git-info', required=False, default=False,
                        help='If true, append info about the latest git commit.')

    args = parser.parse_args()

    files = find_files(directory=args.directory, patterns=args.patterns)
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
