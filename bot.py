import os
import discord
from discord.ext import tasks, commands
import feedparser

# Load your bot token from the hosting environment
TOKEN = os.getenv('DISCORD_TOKEN')

# Replace with your actual #normalsville-post Channel ID (Numbers only)
CHANNEL_ID = 123456789012345678

# URL for Normalsville's RSS feed on ComicFury
RSS_URL = 'https://normalsville.the-comic.org/rss/'

# Initialize bot with default intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Track the last seen comic URL to avoid posting duplicates
last_seen_comic = None

@bot.event
async def on_ready():
    print(f'Logged in successfully as {bot.user.name} ({bot.user.id})')
    # Start the background checking loop when the bot connects
    check_new_comic.start()

@tasks.loop(minutes=15)
async def check_new_comic():
    global last_seen_comic

    try:
        # Parse the webcomic RSS feed
        feed = feedparser.parse(RSS_URL)

        if feed.entries:
            latest_entry = feed.entries[0]
            latest_link = latest_entry.link
            latest_title = latest_entry.title

            # On initial startup, set the current latest comic without spamming the channel
            if last_seen_comic is None:
                last_seen_comic = latest_link
                print(f"Initial feed check complete. Latest comic: {latest_title}")
                return

            # If a new entry is detected
            if latest_link != last_seen_comic:
                last_seen_comic = latest_link
                channel = bot.get_channel(CHANNEL_ID)

                if channel:
                    await channel.send(
                        f"🎨 **New Normalsville Comic Posted!**\n"
                        f"**{latest_title}**\n"
                        f"{latest_link}"
                    )
                    print(f"Posted new comic to Discord: {latest_title}")
                else:
                    print(f"Error: Could not find channel with ID {CHANNEL_ID}")

    except Exception as e:
        print(f"Error checking RSS feed: {e}")

@check_new_comic.before_loop
async def before_check():
    # Wait until the bot is fully logged in before running the task loop
    await bot.wait_until_ready()

# Run the bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: DISCORD_TOKEN environment variable not found.")
