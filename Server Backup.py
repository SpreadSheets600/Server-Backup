import io
import discord
import aiohttp
from discord.ext import commands

TOKEN = "BOT TOKEN"

BACKUP_CATEGORY_PREFIX = "Backup" 

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

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

async def backup_server(guild, backup_category):
    for category in guild.categories:
        for channel in category.channels:
            if isinstance(channel, discord.TextChannel):

                backup_channel_name = f"{category.name}-{channel.name}"
                backup_channel = discord.utils.get(
                    backup_category.channels, name=backup_channel_name
                )
                if backup_channel is None:
                    backup_channel = await backup_category.create_text_channel(
                        name=backup_channel_name
                    )

                await backup_channel.purge()
                await copy_old_messages(channel, backup_channel)

async def copy_old_messages(source_channel, target_channel):
    async for message in source_channel.history(limit=None, oldest_first=True):
        await send_message_with_attachments(target_channel, message)

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

bot.run(TOKEN)
