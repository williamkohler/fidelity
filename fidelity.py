import discord
from discord.ext import commands

# Set up the bot with a command prefix
bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world!")

# Run the bot using your token
bot.run('YOUR_DISCORD_BOT_TOKEN_HERE')
