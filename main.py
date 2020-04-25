import discord
import config

client = discord.Client()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

if __name__ == "__main__":
    client.run( config.DISCORD_BOT_TOKEN )
