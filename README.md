# Telegram Upload [![Test Action](https://github.com/PonomarevDA/telegram-upload/actions/workflows/test.yml/badge.svg)](https://github.com/PonomarevDA/telegram-upload/actions/workflows/test.yml)

A GitHub Action to upload one or more files (e.g., `.bin`, `.elf`, logs, etc.) to a Telegram chat via a bot token. This helps streamline the distribution of build artifacts or release files to Telegram.

## Features

- Uploads multiple files at once using Telegram’s `sendMediaGroup`.
- Support for custom [glob patterns](https://en.wikipedia.org/wiki/Glob_(programming)) (e.g., `"*.bin" "*.elf"`).
- Appends optional Git commit info for auditing (`add_git_info`).
- Simple to integrate into any GitHub workflow.

## Usage

1. **Add a Step in Your Workflow**

   ```yaml
   - name: Deploy to Telegram
     uses: PonomarevDA/telegram-upload@v1.0.0
     with:
       bot_token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
       chat_id: ${{ secrets.TELEGRAM_CHAT_ID }}
       directory: build/release
       patterns: "*.bin *.elf"
       message: "Deployment from GitHub Actions"
       add_git_info: "true"
    ```

**Where to Get These Inputs**

- `bot_token`: Create a Telegram bot via @BotFather and copy the token.
- `chat_id`: The numeric chat/channel/group ID where you want to send files. You can use @get_id_bot or similar to find it.

**Secrets Configuration**

- Go to your repository’s Settings > Secrets and variables > Actions and add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` with appropriate values.
- Reference them in your workflow using ${{ secrets.`TELEGRAM_BOT_TOKEN` }} / ${{ secrets.`TELEGRAM_CHAT_ID` }}.

## Inputs

| Input | Required | Default | Description |
|-|-|-|-|
| bot_token | Yes | – | Your Telegram bot token. |
| chat_id | Yes | –	| The ID of the Telegram chat/channel/group where files are sent. |
| directory | Yes | – | The directory containing files to upload. |
| patterns | No | *.bin | One or more glob patterns (space-separated) to match files (e.g. "*.bin *.elf").
| message | Yes | – | The caption text for the final file. (It’s appended as a caption to the last file in the media group.) |
| add_git_info | No | false | If "true", appends Git commit info (commit SHA, author, date) to the message. |

## Notes & Limitations

- Telegram’s sendMediaGroup only supports up to 10 files in a single request. If more than 10 files match, the action currently logs an error and exits.
- Telegram enforces a per-file size limit (commonly up to 2GB).
