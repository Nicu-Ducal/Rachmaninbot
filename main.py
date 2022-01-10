import os
import discord
from discord.ext import commands
from musicbot import MusicBot
from server import keep_alive

# Bot client
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='-', intents=intents)

@client.event
async def on_ready():
    print(f"{client.user.name} is ready.")

async def setup():
    await client.wait_until_ready()
    client.add_cog(MusicBot(client))

# Keep the server alive to keep the bot alive by sending repeating requests
keep_alive()

# Start the Discord Music Bot
client.loop.create_task(setup())
client.run(os.getenv("TOKEN"))