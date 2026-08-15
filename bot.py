import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import tasks, commands
import feedparser

# --- Tiny Web Server for Render Free Tier ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- Discord Bot Code ---
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1537894788962193408
RSS_URL = 'https://normalsville.the-comic.org/rss/'

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
last_seen_comic = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}', flush=True)
    if not check_new_comic.is_running():
        check_new_comic.start()

@tasks.loop(minutes=15)
async def check_new_comic():
    global last_seen_comic
    try:
        print("Checking RSS feed...", flush=True)
        feed = feedparser.parse(RSS_URL)
        
        if feed.entries:
            latest_entry = feed.entries[0]
            latest_link = latest_entry.link
            latest_title = latest_entry.title
            print(f"Fetched latest comic link: {latest_link}", flush=True)

            if latest_link != last_seen_comic:
                last_seen_comic = latest_link
                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    await channel.send(f"🎨 **New Normalsville Comic Posted!**\n**{latest_title}**\n{latest_link}")
                    print("Successfully sent message to Discord!", flush=True)
                else:
                    print(f"Error: Channel {CHANNEL_ID} not found. Check bot permissions.", flush=True)
            else:
                print("No new comic found since last check.", flush=True)
    except Exception as e:
        print(f"Error checking feed: {e}", flush=True)

@check_new_comic.before_loop
async def before_check():
    await bot.wait_until_ready()

if TOKEN:
    bot.run(TOKEN)
