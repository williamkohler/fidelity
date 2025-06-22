import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world!")

bot.run(TOKEN)
