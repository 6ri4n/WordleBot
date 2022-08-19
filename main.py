import asyncio
import random
import time
import discord
from discord.ext import commands

from WordleClass.wordle import WordleClass


bot = commands.Bot(command_prefix = ".", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"\nONLINE\nLogged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name = "Wordle"))

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)
    else:
        raise error

@bot.slash_command(guild_ids=[1009167894573219943], description = "play wordle against an AI")
@commands.cooldown(1, 5, commands.BucketType.user) # 5 sec cd for ease of testing
async def play(ctx):
    # TODO: set the correct 5-letter word
    game = WordleClass()
    correct_word = game.get_random_word()

    # TODO: randomly pick who goes first - player or AI
    # 1 - player, odds, 2 - AI, evens
    # TODO: random later - random.choice([1,2])
    player_turn = 1 # 1 for now for testing

    await ctx.send("game starting in 5 seconds", delete_after = 5.0)
    time.sleep(5)

    # game when in progress is true otherwise false when game ends
    game_state = True
    while game_state and player_turn < 13:
        try:
            # TODO: turn based system
            # player turn
            if player_turn % 2 != 0:
                await ctx.send(str(player_turn) + " player turn")
                def check(message):
                    return len(message.content) == 5 and message.author == ctx.author
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
@commands.cooldown(1, 5, commands.BucketType.user)
async def grid(ctx):
    game = WordleClass()
    await ctx.respond(game.display_game_grid(1))

    await ctx.respond(game.display_game_grid(2))


@bot.slash_command(guild_ids=[1009167894573219943], description = "how-to-play wordle")
@commands.cooldown(1, 60, commands.BucketType.user)
async def help(ctx):
    # TODO: send embed message that introduces the game, how-to-play page
    help_message = discord.Embed(
            title = "how-to-play",
            description = ("- you have six attempts to guess the word correctly\n\n"
                           "- each guess must be a valid five-letter word in the dictionary\n\n"
                           "- after each guess, the color of the tiles will change to show how close your guess was to the correct word\n\n"
                           "- the AI will win by default if you cannot guess the correct word\n\n"
                           "tile indicators:\n"
                           "🟩 - the letter is in the word and in the correct spot\n"
                           "🟨 - the letter is in the word but in the incorrect spot\n"
                           "⬛ - the letter is not in the word"
                        ),
            color = discord.Color.from_rgb(138, 134, 135)
        )
    help_message.set_footer(text = f"{ctx.user.name}#{ctx.user.discriminator}")

    await ctx.respond(embed = help_message)

@bot.slash_command(guild_ids=[1009167894573219943], description = "test color tile indicators")
@commands.cooldown(1, 60, commands.BucketType.user)
async def color(ctx):
    # TODO: test color tile indicators
    game = WordleClass()
    game.check_guess("horse", "hence", 1)
    await ctx.send(game.display_game_grid(1))

    game.check_guess("fence", "hence", 2)
    await ctx.send(game.display_game_grid(2))

token = open("token.txt", "r")
bot.run(token.read())