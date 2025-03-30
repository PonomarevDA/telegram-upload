#!/usr/bin/env python3
"""
Send a group of files to a Telegram chat using a bot token.
"""
import sys
import logging
import argparse
import subprocess
from pathlib import Path
from typing import List
import requests


logger = logging.getLogger("deploy_files_to_telegram.py")

def get_git_info() -> str:
    """
    Return a string summarizing the current Git commit.
    """

    def run_git_command(args):
        """Helper to run a git command and return stripped string output, or None on failure."""
        return subprocess.check_output(args).decode('utf-8').strip()


    try:
        commit_sha = run_git_command(['git', 'rev-parse', '--short=8', 'HEAD'])
        commit_date = run_git_command(['git', 'log', '-1', '--format=%cd', '--date=short'])
        committer_name = run_git_command(['git', 'log', '-1', '--format=%an'])
        committer_email = run_git_command(['git', 'log', '-1', '--format=%ae'])
        branch_name = run_git_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])

        try:
            latest_tag = run_git_command(['git', 'describe', '--tags', '--abbrev=0'])
        except subprocess.CalledProcessError:
            latest_tag = "not tagged"

        git_info = (
            f"VCS commit: {commit_sha}\n"
            f"Commit date: {commit_date}\n"
            f"Author: {committer_name} <{committer_email}>\n"
            f"Branch: {branch_name}\n"
            f"Latest Tag: {latest_tag}\n"
        )
    except subprocess.CalledProcessError:
        git_info = "Could not retrieve Git commit info. Are you in a Git repo?"
        logger.error(git_info)

    return git_info

def resolve_files(file_inputs: List[str]) -> List[Path]:
    """
    Given a list of file paths or glob patterns, return a sorted, unique list of valid Paths.
    Example: ["build/*.bin", "myapp.elf", "docs/readme.md"]
    """
    all_matched = []

    for pattern in file_inputs:
        # Use glob from the current working directory
        matched = list(Path().glob(pattern))
        if not matched:
            # If the glob found nothing, check if 'pattern' is a literal file path
            possible_path = Path(pattern)
            if possible_path.exists():
                matched = [possible_path]

        all_matched.extend(matched)

    # Remove duplicates, sort
    unique_files = sorted(set(all_matched))
    if not unique_files:
        raise FileNotFoundError(f"No files found for patterns: {file_inputs}")

    return unique_files

def send_media_group(telegram_bot_token: str,
                     telegram_chat_id: str,
                     files: List[Path],
                     caption: str) -> None:
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
        sys.exit(1)

    if len(files) > 10:
        logger.error("Too many files to send")
        sys.exit(1)

    media_json_array = [None] * len(files)

    for idx in range(0, len(files) - 1):
        media_json_array[idx] = {"type": "document", "media": f"attach://file{idx + 1}"}

    media_json_array[len(files) - 1] = {
        "type": "document",
        "media": f"attach://file{len(files)}",
        "caption": caption
    }

    media_payload = {
        'chat_id': telegram_chat_id,
        'media': str(media_json_array).replace("'", '"')
    }

    files_payload = {}
    for idx in range(len(files)):
        files_payload[f"file{idx + 1}"] = open(files[idx], 'rb')

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMediaGroup"
    response = requests.post(url, data=media_payload, files=files_payload, timeout=5)

    for file in files_payload.values():
        file.close()

    try:
        response.json()
    except ValueError:
        logger.error(
            "Telegram API returned non-JSON or invalid JSON (status %s): %s",
            response.status_code, response.text
        )
        sys.exit(1)

    if response.status_code != 200:
        logger.error(
            "Telegram API call failed (HTTP %d). Response text: %s",
            response.status_code, response.text
        )
        sys.exit(1)

    logger.info("Files have been send.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bot-token', required=True, help='Telegram bot token')
    parser.add_argument('--chat-id', required=True, help='Telegram chat ID')
    parser.add_argument('--files', nargs='+', required=True,
                        help='One or more file paths or glob patterns (e.g. "build/*.bin" "my_firmware.elf")')

    parser.add_argument('--message', required=True)
    parser.add_argument('--add-git-info', required=False, default=False,
                        help='If true, append info about the latest git commit.')

    args = parser.parse_args()

    # Resolve the user-provided file inputs
    try:
        resolved_files = resolve_files(args.files)
    except (ValueError, FileNotFoundError) as e:
        logger.error(str(e))
        sys.exit(1)

    # Build final message
    message = f"{args.message}\n"
    if args.add_git_info.strip().lower() in ["true", "1", "yes", "on"]:
        message += get_git_info()

    send_media_group(args.bot_token, args.chat_id, resolved_files, message)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)

    main()
