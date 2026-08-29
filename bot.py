import os
import asyncio
import discord
from discord.ext import commands, tasks
import feedparser
from aiohttp import web

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

TARGET_CHANNELS = [
    1538994462318006323,  # Server 1
    1538994665838084207   # Server 2
]

# Set higher than MAX_ARCHIVE_COMIC to mark the archive as complete
CURRENT_COMIC_NUM = 478
MAX_ARCHIVE_COMIC = 476
RSS_FEED_URL = "https://normalsville.the-comic.org/rss/"
LAST_POSTED_LINK = "https://normalsville.the-comic.org/comics/477/#content-start"

async def safe_send(channel_id: int, message: str):
    """Helper function to fetch channel and send message reliably."""
    try:
        channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
        if channel:
            await channel.send(message)
    except Exception as e:
        print(f"Failed to send to channel {channel_id}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Archive is finished, launch live check directly
    if not check_new_comics.is_running():
        check_new_comics.start()

@tasks.loop(minutes=10)
async def check_new_comics():
    global LAST_POSTED_LINK
    feed = feedparser.parse(RSS_FEED_URL)
    
    if feed.entries:
        latest_entry = feed.entries[0]

        # Only post if the link in RSS is newer than comic #477
        if LAST_POSTED_LINK != latest_entry.link:
            for channel_id in TARGET_CHANNELS:
                await safe_send(channel_id, f"**New Comic Released!** {latest_entry.link}")
            LAST_POSTED_LINK = latest_entry.link

async def handle_ping(request):
    return web.Response(text="Bot is online!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    async with bot:
        await start_web_server()
        await bot.start(os.getenv("TOKEN"))

asyncio.run(main())
