import os
import discord
from discord.ext import commands, tasks
import feedparser

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

# Channel IDs for Server 1 and Server 2
TARGET_CHANNELS = [
    1538994462318006323,  # Server 1
    1538994665838084207   # Server 2
]

CURRENT_COMIC_NUM = 1
MAX_ARCHIVE_COMIC = 476
RSS_FEED_URL = "https://normalsville.the-comic.org/rss/"
LAST_POSTED_LINK = None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not post_archive.is_running():
        post_archive.start()

# Loop 1: Post past archive comics every 10 seconds to all channels
@tasks.loop(seconds=10)
async def post_archive():
    global CURRENT_COMIC_NUM

    if CURRENT_COMIC_NUM <= MAX_ARCHIVE_COMIC:
        comic_url = f"https://normalsville.the-comic.org/comics/{CURRENT_COMIC_NUM}/"
        for channel_id in TARGET_CHANNELS:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(f"**Archive Comic #{CURRENT_COMIC_NUM}:** {comic_url}")
        CURRENT_COMIC_NUM += 1
    else:
        print("Archive catch-up complete! Switching to live RSS checking...")
        post_archive.stop()
        if not check_new_comics.is_running():
            check_new_comics.start()

# Loop 2: Check RSS feed every 10 minutes and post new comics to all channels
@tasks.loop(minutes=10)
async def check_new_comics():
    global LAST_POSTED_LINK
    feed = feedparser.parse(RSS_FEED_URL)
    
    if feed.entries:
        latest_entry = feed.entries[0]
        if LAST_POSTED_LINK != latest_entry.link:
            if LAST_POSTED_LINK is not None:
                for channel_id in TARGET_CHANNELS:
                    channel = bot.get_channel(channel_id)
                    if channel:
                        await channel.send(f"**New Comic Released!** {latest_entry.link}")
            LAST_POSTED_LINK = latest_entry.link

bot.run(os.getenv("TOKEN"))
