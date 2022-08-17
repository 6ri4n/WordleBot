import asyncio
import random
import discord
from discord.ext import commands

from WordleClass.wordle import WordleClass


bot = commands.Bot(command_prefix = ".", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)
    else:
        raise error

@bot.slash_command(guild_ids=[1009167894573219943], description = "play wordle against an AI")
@commands.cooldown(1, 1, commands.BucketType.user) # 1 sec cd for ease of testing
async def play(ctx):
    # TODO: set the correct 5-letter word
    game = WordleClass()
    correct_word = game.get_random_word()

    # TODO: randomly pick who goes first - player or AI
    # 1 - player goes first, 2 - AI goes first
    # 1 - player, odds, 2 - AI, evens
    player_turn = 1 # 1 for now for testing
    # do random later - random.choice([1,2])

    def check(message):
            return message.author == ctx.author

    # game when in progress is true otherwise false when game ends
    await ctx.respond("game started")
    game_state = True
    while game_state and player_turn < 13:
        try:
            # TODO: turn based system
            # player turn
            if player_turn % 2 != 0:
                await ctx.send(str(player_turn) + " player turn")
                player_guess = await bot.wait_for("message", timeout = 5.0, check = check)
                await ctx.send(player_guess.content.lower())
                player_turn += 1
            # AI turn
            else:
                await ctx.send(str(player_turn) + " AI turn")
                await ctx.send("AI turn completed")
                player_turn += 1
        # time out after player inactivity
        except asyncio.TimeoutError:
            game_state = False
            await ctx.send("game timed out")


    await ctx.send("game completed")




@bot.slash_command(guild_ids=[1009167894573219943], description = "play wordle against an AI")
@commands.cooldown(1, 1, commands.BucketType.user) # 1 sec cd for ease of testing
async def grid(ctx):
    game = WordleClass()
    await ctx.respond(game.display_game_grid(1))

    await ctx.respond(game.display_game_grid(2))







token = open("token.txt", "r")
bot.run(token.read())