# Telegram Upload [![Test Action](https://github.com/PonomarevDA/telegram-upload/actions/workflows/tests.yml/badge.svg)](https://github.com/PonomarevDA/telegram-upload/actions/workflows/tests.yml)

A GitHub Action to upload one or more files (e.g., `.bin`, `.elf`, logs, etc.) to a Telegram chat via a bot token. This helps streamline the distribution of build artifacts or release files to Telegram.

## Usage

```yaml
- uses: PonomarevDA/telegram-upload@v1.1.0
  with:
    # Your Telegram bot token.
    # Create a Telegram bot via @BotFather,
    # Go to your repository’s Settings > Secrets > Actions > New repository secret
    # Add TELEGRAM_BOT_TOKEN with the value of the token.
    bot_token: ${{ secrets.TELEGRAM_BOT_TOKEN }}

    # The ID of the Telegram chat/channel/group where files are sent.
    # Use @get_id_bot, https://api.telegram.org/bot<token>/getUpdates to find it.
    chat_id: ${{ secrets.TELEGRAM_CHAT_ID }}

    # One or more file paths or glob patterns (e.g. "build/*.bin" "my_firmware.elf")"
    files: build/release/*.bin

    # The caption text for the final file.
    # It’s appended as a caption to the last file in the media group.
    message: "Deployment from GitHub Actions"

    # If "true", automatically appends Git commit info to the message. Like this:
    # VCS commit: 75fdf50
    # Commit date: 2025-03-30
    # Author: author <email>
    # Branch: main
    # Latest Tag: v1.0.0
    add_git_info: "true"
```

## Notes & Limitations

- Telegram’s sendMediaGroup only supports up to 10 files in a single request. If more than 10 files match, the action currently logs an error and exits.
- Telegram enforces a per-file size limit (commonly up to 2GB).
