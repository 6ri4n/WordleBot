import discord
from discord.ext import commands

bot = commands.Bot(command_prefix = ".")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)
    else:
        raise error

@bot.slash_command(guild_ids=[1009167894573219943], description = "🧠 vs 🤖")
@commands.cooldown(1, 1, commands.BucketType.user) # 1 sec cd for ease of testing
async def wordle(ctx):
    await ctx.respond("hello world")















token = open("token.txt", "r")
bot.run(token.read())