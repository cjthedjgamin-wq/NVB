import asyncio
import os
import discord
from discord.ext import commands, tasks
import feedparser

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

CHANNEL_ID = 1538989136898424931  # Replace with your actual channel ID
CURRENT_COMIC_NUM = 1
MAX_ARCHIVE_COMIC = 476
RSS_FEED_URL = "https://normalsville.the-comic.org/rss/"
LAST_POSTED_LINK = None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not post_archive.is_running():
        post_archive.start()

# Loop 1: Post through the archive every 10 seconds
@tasks.loop(seconds=10)
async def post_archive():
    global CURRENT_COMIC_NUM
    channel = bot.get_channel(CHANNEL_ID)

    if channel and CURRENT_COMIC_NUM <= MAX_ARCHIVE_COMIC:
        comic_url = f"https://normalsville.the-comic.org/comics/{CURRENT_COMIC_NUM}/"
        await channel.send(f"**Archive Comic #{CURRENT_COMIC_NUM}:** {comic_url}")
        CURRENT_COMIC_NUM += 1
    else:
        print("Archive catch-up complete! Switching to live RSS checking...")
        post_archive.stop()
        if not check_new_comics.is_running():
            check_new_comics.start()

# Loop 2: Runs only after archive finishes, checks RSS feed every 10 minutes
@tasks.loop(minutes=10)
async def check_new_comics():
    global LAST_POSTED_LINK
    channel = bot.get_channel(CHANNEL_ID)
    feed = feedparser.parse(RSS_FEED_URL)
    
    if feed.entries:
        latest_entry = feed.entries[0]
        if LAST_POSTED_LINK != latest_entry.link:
            # If it's the first time running, set the link so it doesn't duplicate
            if LAST_POSTED_LINK is not None:
                await channel.send(f"**New Comic Released!** {latest_entry.link}")
            LAST_POSTED_LINK = latest_entry.link

bot.run(os.getenv("TOKEN"))  # Or replace with "YOUR_BOT_TOKEN"
