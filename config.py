import os

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
base_dir = os.path.dirname(os.path.realpath(__file__))
SQLITE_PATH = os.path.join( base_dir, "app.db" )
BOT_PREFIX = os.getenv('DISCORD_BOT_PREFIX', '.')
