import asyncio
import random
import time
import discord
from discord import Option
from discord.ext import commands
from WordleClass.wordle import WordleClass

bot = commands.Bot(command_prefix = ".", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"\nONLINE\nLogged in as {bot.user}\n")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name = "Wordle"))

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)
    else:
        raise error

@bot.slash_command(guild_ids=[1009167894573219943], description = "play wordle against an AI")
@commands.cooldown(1, 5, commands.BucketType.user) # TODO: change later - set 5 sec cd for ease of testing
async def play(ctx, difficulty: Option(str, 'modes: test, easy, normal, hard', required = True)):
    # randomly set a 5-letter word that the player and ai is supposed to guess
    game = WordleClass()
    actual_word = 'hence' #game.get_random_word()

    # player goes first
    player_turn = 1

    # setup start message
    start_message = discord.Embed(
        title = 'game will begin in 5 seconds.',
        color = discord.Color.from_rgb(59,136,195)
        )
    start_message.set_footer(text = f"{ctx.user.name}#{ctx.user.discriminator}")
    # display start message
    await ctx.respond(embed = start_message, delete_after = 5.0)

    def check(message):
        return len(message.content) == 5 and message.author == ctx.author
    # game progress
    in_progress = True
    timeout = False
    # winner/loser/draw
    game_status = 'draw'
    # setup invalid message
    invalid_message = discord.Embed(
        title = 'invalid word, please try again.',
        color = discord.Color.from_rgb(59,136,195)
    )
    invalid_message.set_footer(text = f"{ctx.user.name}#{ctx.user.discriminator}")

    time.sleep(5)
    print('game start')
    base_game_message = await ctx.send(game.display_game_grid(player_turn, game_status))
    while in_progress and player_turn < 13:
        try:
            # TODO: implement turn based
            # turns - player is odd, AI is even
            if player_turn % 2 != 0:
                # player turn
                player_guess = await bot.wait_for("message", timeout = 10.0, check = check)
                # waits until a valid guess is given
                #print('player guess: ' + player_guess.content.lower())
                #print('check: ' + str(game.check_guess(player_guess.content.lower(), actual_word, player_turn)))
                #print('comparison: ' + str(not game.check_guess(player_guess.content.lower(), actual_word, player_turn)))
                while not game.check_guess(player_guess.content.lower(), actual_word, player_turn):
                    # display invalid message
                    await ctx.send(embed = invalid_message, delete_after = 3.5)
                    player_guess = await bot.wait_for("message", timeout = 10.0, check = check)
                # delete the player's guess
                await player_guess.delete()
                # check if the guess matches the word
                if game.check_for_win(player_turn) == 'player':
                    game_status = 'player'
                    in_progress = False
            else:
                # AI turn
                time.sleep(3)
                if game.check_for_win(player_turn) == 'ai':
                    game_status = 'ai'
                    in_progress = False
            # continue to next turn
            player_turn += 1
            await base_game_message.edit(game.display_game_grid(player_turn, game_status))
        # time out after player inactivity
        except asyncio.TimeoutError:
            in_progress = False
            timeout = True
            await ctx.send("game timed out due to player inactivity")
    print('game completed')
    # game completed
    # display end messages - actual word and winner/loser/draw
    if timeout == False:
        actual_word_message = discord.Embed(
            title = 'correct word: ' + '||' + actual_word + '||',
            color = discord.Color.from_rgb(59,136,195)
        )
        actual_word_message.set_footer(text = f"{ctx.user.name}#{ctx.user.discriminator}")
        # show the actual word after match ends
        await ctx.send('correct word: ' + '||' + actual_word + '||')
        # show winner/loser/draw message
        if game_status == 'player':
            end_message = discord.Embed(
                title = 'Victory! 👤 🏆',
                color = discord.Color.from_rgb(59,136,195)
            )
            end_message.set_footer(text = f"{ctx.user.name}#{ctx.user.discriminator}")
            await ctx.send(embed = end_message)
        elif game_status == 'ai':
            end_message = discord.Embed(
                title = 'Victory! 🤖 🏆',
                color = discord.Color.from_rgb(59,136,195)
            )
            end_message.set_footer(text = f"{ctx.user.name}#{ctx.user.discriminator}")
            await ctx.send(embed = end_message)
        else:
            end_message = discord.Embed(
                title = 'Draw! 👤 🤝 🤖',
                color = discord.Color.from_rgb(59,136,195)
            )
            end_message.set_footer(text = f"{ctx.user.name}#{ctx.user.discriminator}")
            await ctx.send(embed = end_message)

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
            color = discord.Color.from_rgb(59,136,195)
        )
    help_message.set_footer(text = f"{ctx.user.name}#{ctx.user.discriminator}")

    await ctx.respond(embed = help_message)

@bot.slash_command(guild_ids=[1009167894573219943], description = "testing")
@commands.cooldown(1, 5, commands.BucketType.user)
async def test_play(ctx):
    # TODO: test color tile indicators
    game = WordleClass()
    print('player turn:')
    game.check_guess("horse", "hence", 1)
    await ctx.send(game.display_game_grid(1))
    print('ai turn:')
    game.check_guess("fence", "hence", 2)
    await ctx.send(game.display_game_grid(2))
    print('player turn:')
    game.check_guess("hange", "hence", 3)
    await ctx.send(game.display_game_grid(3))
    print('ai turn:')
    game.check_guess("power", "hence", 4)
    await ctx.send(game.display_game_grid(4))

token = open("token.txt", "r")
bot.run(token.read())