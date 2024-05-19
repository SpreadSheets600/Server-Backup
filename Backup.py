import io
import discord
import aiohttp
from discord.ext import commands

# Replace 'YOUR_BOT_TOKEN' with your bot's token
TOKEN = ''


SOURCE_CATEGORY_ID = 1229465129939239023
TARGET_CATEGORY_ID = 1241788534315159602

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    source_category = discord.utils.get(bot.get_all_channels(), id=SOURCE_CATEGORY_ID)
    target_category = discord.utils.get(bot.get_all_channels(), id=TARGET_CATEGORY_ID)
    if source_category is None:
        print(f'Could not find the source category with ID {SOURCE_CATEGORY_ID}')
    if target_category is None:
        print(f'Could not find the target category with ID {TARGET_CATEGORY_ID}')
    await copy_old_messages_from_category(source_category, target_category)

async def copy_old_messages_from_category(source_category, target_category):
    if source_category is None or target_category is None:
        return
    
    for source_channel in source_category.channels:
        if isinstance(source_channel, discord.TextChannel):
            target_channel = discord.utils.get(target_category.channels, name=source_channel.name)
            if target_channel is None:

                target_channel = await target_category.create_text_channel(name=source_channel.name)
            
            async for message in source_channel.history(limit=None, oldest_first=True):
                await send_message_with_attachments(target_channel, message)

async def send_message_with_attachments(channel, message):
    files = []
    for attachment in message.attachments:
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as response:
                if response.status == 200:
                    data = await response.read()
                    files.append(discord.File(io.BytesIO(data), filename=attachment.filename))
    
    await channel.send(content=f'{message.author}: {message.content}', files=files)

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return
    
    source_category = discord.utils.get(bot.get_all_channels(), id=SOURCE_CATEGORY_ID)
    target_category = discord.utils.get(bot.get_all_channels(), id=TARGET_CATEGORY_ID)
    if source_category is None or target_category is None:
        return

    if message.channel.category_id == SOURCE_CATEGORY_ID:

        target_channel = discord.utils.get(target_category.channels, name=message.channel.name)
        if target_channel is None:

            target_channel = await target_category.create_text_channel(name=message.channel.name)

        await send_message_with_attachments(target_channel, message)

    await bot.process_commands(message)

# Run the bot
bot.run(TOKEN)
