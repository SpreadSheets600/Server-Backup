import io
import discord
import aiohttp
from discord.ext import commands

TOKEN = "BOT TOKEN"

SOURCE_CATEGORY_ID = 1241783365389123625 # Source Category ID - Which You Want To Copy
TARGET_CATEGORY_ID = 1234744396872679445 # Target Category ID - Where You Want To Copy

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():

    print("------------------------------------------------------")
    print(f"Logged In As : {bot.user}")
    print("------------------------------------------------------")

    source_category = discord.utils.get(bot.get_all_channels(), id=SOURCE_CATEGORY_ID)
    target_category = discord.utils.get(bot.get_all_channels(), id=TARGET_CATEGORY_ID)

    if source_category is None:
        print(f"[ ERR ] Source Category Not Found - {SOURCE_CATEGORY_ID}")

    if target_category is None:
        print(f"[ ERR ] Target Category Not Found - {TARGET_CATEGORY_ID}")

    await copy_old_messages_from_category(source_category, target_category)


async def copy_old_messages_from_category(source_category, target_category):
    if source_category is None or target_category is None:
        return

    for source_channel in source_category.channels:
        if isinstance(source_channel, discord.TextChannel):
            target_channel = discord.utils.get(
                target_category.channels, name=source_channel.name
            )
            if target_channel is None:

                target_channel = await target_category.create_text_channel(
                    name=source_channel.name
                )

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

    source_category = discord.utils.get(bot.get_all_channels(), id=SOURCE_CATEGORY_ID)
    target_category = discord.utils.get(bot.get_all_channels(), id=TARGET_CATEGORY_ID)
    if source_category is None or target_category is None:
        return

    if message.channel.category_id == SOURCE_CATEGORY_ID:

        target_channel = discord.utils.get(
            target_category.channels, name=message.channel.name
        )
        if target_channel is None:

            target_channel = await target_category.create_text_channel(
                name=message.channel.name
            )

        await send_message_with_attachments(target_channel, message)

    await bot.process_commands(message)

bot.run(TOKEN)
