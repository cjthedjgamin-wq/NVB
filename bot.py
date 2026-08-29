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

RSS_FEED_URL = "https://normalsville.the-comic.org/rss/"
LAST_POSTED_ID = None

async def safe_send(channel_id: int, message: str):
    """Helper function to fetch channel and send message reliably."""
    try:
        channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
        if channel:
            await channel.send(message)
    except Exception as e:
        print(f"Failed to send to channel {channel_id}: {e}")

def get_entry_identifier(entry):
    """Returns unique entry identifier (guid or link)."""
    return getattr(entry, 'id', entry.link)

@bot.event
async def on_ready():
    global LAST_POSTED_ID
    print(f"Logged in as {bot.user}")
    
    # Initialize LAST_POSTED_ID from feed on boot to prevent startup double-posting
    try:
        feed = feedparser.parse(RSS_FEED_URL)
        if feed.entries:
            LAST_POSTED_ID = get_entry_identifier(feed.entries[0])
            print(f"Initialized latest RSS entry ID: {LAST_POSTED_ID}")
    except Exception as e:
        print(f"Failed to fetch initial feed: {e}")

    if not check_new_comics.is_running():
        check_new_comics.start()

@tasks.loop(minutes=1)
async def check_new_comics():
    global LAST_POSTED_ID
    feed = feedparser.parse(RSS_FEED_URL)
    
    if feed.entries:
        latest_entry = feed.entries[0]
        current_id = get_entry_identifier(latest_entry)

        if LAST_POSTED_ID != current_id:
            comic_url = latest_entry.link
            
            # If the RSS feed outputs a generic home link, append the entry title or specific target
            for channel_id in TARGET_CHANNELS:
                await safe_send(channel_id, f"**New Comic Released!** {comic_url}")
            
            LAST_POSTED_ID = current_id

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
