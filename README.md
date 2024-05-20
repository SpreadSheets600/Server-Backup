# Discord Server Backup Bot

A Discord bot that backs up all text channels in every server it is part of, including messages and attachments, and stores them in a separate backup category for each server.

## Features

- Backs up all text channels in every server the bot is in.
- Copies messages and attachments from the original channels to the backup channels.
- Creates unique backup categories for each server to avoid conflicts.
- Supports real-time backup of new messages as they are sent.
- Clears existing messages in backup channels before copying new ones to avoid duplicates.

## Requirements

- Python 3.8+
- `discord.py` library
- `aiohttp` library

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/discord-backup-bot.git
   cd discord-backup-bot
  
2. Install the required Python packages:
   ```sh
   pip install discord.py aiohttp
   ```

3. Create a new file named `.env` and add your bot token:
   ```
   TOKEN=YOUR_BOT_TOKEN
   ```

4. Replace `YOUR_BOT_TOKEN` with your actual bot token.

## Usage

1. Run the bot:
   ```sh
   python Server Backup.py
   ```

2. The bot will automatically back up all text channels in every server it is part of, creating a unique backup category for each server.

## Bot Commands

Currently, the bot does not have any specific commands. It performs the backup operation automatically upon startup and in real-time as new messages are sent.

## Code Explanation

Here's a brief overview of the main components of the bot:

### `on_ready` Event

This event triggers when the bot successfully connects to Discord. It iterates through all servers the bot is in and initiates the backup process for each server:

```python
@bot.event
async def on_ready():
    print("------------------------------------------------------")
    print(f"Logged In As : {bot.user}")
    print("------------------------------------------------------")

    for guild in bot.guilds:
        backup_category_name = f"{BACKUP_CATEGORY_PREFIX} {guild.name}"
        backup_category = discord.utils.get(guild.categories, name=backup_category_name)
        if backup_category is None:
            backup_category = await guild.create_category(backup_category_name)

        await backup_server(guild, backup_category)
```

### `backup_server` Function

This function iterates through all categories and channels in a server, creating corresponding backup channels in the backup category and copying messages:

```python
async def backup_server(guild, backup_category):
    for category in guild.categories:
        for channel in category.channels:
            if isinstance(channel, discord.TextChannel):
                # Create or get the corresponding backup channel
                backup_channel_name = f"{category.name}-{channel.name}"
                backup_channel = discord.utils.get(
                    backup_category.channels, name=backup_channel_name
                )
                if backup_channel is None:
                    backup_channel = await backup_category.create_text_channel(
                        name=backup_channel_name
                    )

                await backup_channel.purge()  # Clear any existing messages in the backup channel
                await copy_old_messages(channel, backup_channel)
```

### `copy_old_messages` Function

This function copies all messages from the source channel to the target backup channel:

```python
async def copy_old_messages(source_channel, target_channel):
    async for message in source_channel.history(limit=None, oldest_first=True):
        await send_message_with_attachments(target_channel, message)
```

### `send_message_with_attachments` Function

This function sends messages and attachments to the target channel:

```python
async def send_message_with_attachments(channel, message):
    files = []
    for attachment in message.attachments:
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as response:
                if response.status == 200:
                    data = await response.read()
                    files.append(
                        discord.File(io.BytesIO(data), filename=attachment.filename)
                    )

    await channel.send(content=f"{message.content}", files=files)
```

### `on_message` Event

This event triggers whenever a new message is sent. It checks if the message is in a source channel and copies it to the corresponding backup channel:

```python
@bot.event
async def on_message(message):
    if message.guild is None:
        return

    backup_category_name = f"{BACKUP_CATEGORY_PREFIX} {message.guild.name}"
    backup_category = discord.utils.get(message.guild.categories, name=backup_category_name)
    if backup_category is None:
        return

    if message.channel.category and message.channel.category.name != backup_category_name:
        backup_channel_name = f"{message.channel.category.name}-{message.channel.name}"
        backup_channel = discord.utils.get(
            backup_category.channels, name=backup_channel_name
        )
        if backup_channel is None:
            backup_channel = await backup_category.create_text_channel(
                name=backup_channel_name
            )

        await send_message_with_attachments(backup_channel, message)

    await bot.process_commands(message)
```

## Contributing

Feel free to submit issues or pull requests if you find any bugs or want to add new features.


### How to Customize
- **Repository URL**: Replace `https://github.com/yourusername/discord-backup-bot.git` with the actual URL of your GitHub repository.
- **Bot Token**: Make sure to replace `YOUR_BOT_TOKEN` with your actual bot token.

This `README.md` file provides an overview of the bot, instructions for installation and usage, and a brief explanation of the code.
