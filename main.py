import asyncio
import random
import time
import discord
from discord import Option
from discord.ext import commands
from WordleClass.wordle import WordleClass

server_id_list = [872995966066757673]
bot = commands.Bot(command_prefix = ".", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"\nONLINE\nLogged in as {bot.user}\n")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name = "Wordle"))

@bot.event
async def on_application_command_error(ctx, error):
    player_name_footer = ctx.user.name + '#' + ctx.user.discriminator
    if isinstance(error, commands.CommandOnCooldown):
        invalid_message = discord.Embed(
            title = 'Command on Cooldown, Please Try Again Later',
            color = discord.Color.from_rgb(59,136,195)
        )
        invalid_message.set_footer(text = f"{player_name_footer}")
        await ctx.respond(embed = invalid_message)
    elif isinstance(error, commands.MaxConcurrencyReached):
        invalid_message = discord.Embed(
            title = 'Please Finish Your Current Game',
            color = discord.Color.from_rgb(59,136,195)
        )
        invalid_message.set_footer(text = f"{player_name_footer}")
        await ctx.respond(embed = invalid_message)
    else:
        raise error

@bot.slash_command(guild_ids = server_id_list, description = "play Wordle against an AI")
@commands.max_concurrency(number = 1, per = commands.BucketType.user, wait = False)
async def play(ctx, difficulty: Option(str, 'select the difficulty for the AI', choices = ['normal', 'hard', 'extreme'], required = True)):
    # TODO: play wordle against an AI

    # randomly set a 5-letter word that the player and ai is supposed to guess
    game = WordleClass()
    actual_word = game.get_random_word()

    # player goes first
    player_turn = 1
    player_name_footer = ctx.user.name + '#' + ctx.user.discriminator
    player_name = '<@' + str(ctx.user.id) + '>'

    def check(message):
        return (len(message.content) == 5 and message.author == ctx.author) or (message.content.lower() == 'quit' and message.author == ctx.author)
    # game progress
    in_progress = True
    timeout = False
    # winner/loser/draw
    game_status = 'draw'
    # setup invalid message
    invalid_message = discord.Embed(
        title = 'Invalid Word, Please Try Again',
        color = discord.Color.from_rgb(59,136,195)
    )
    invalid_message.set_footer(text = f"{player_name_footer}")

    print('game start')
    interaction_game_message = await ctx.respond(game.display_game_grid(player_turn, game_status, timeout, player_name, difficulty))
    base_game_message = await interaction_game_message.original_message()
    # determine the difficulty mode
    # extreme will have 4 rows
    if difficulty == 'extreme':
        while in_progress and player_turn < 9:
            try:
                # TODO: implement turn based
                # turns - player is odd, ai is even
                if player_turn % 2 != 0:
                    # player turn
                    player_guess = await bot.wait_for("message", timeout = 60.0, check = check)
                    if player_guess.content.lower() == 'quit':
                        quit_message = discord.Embed(
                            title = 'HAHAHA Quitting because YOU SUCK!?!?! >:)',
                            color = discord.Color.from_rgb(59,136,195)
                        )
                        quit_message.set_footer(text = f"{player_name_footer}")
                        await ctx.send(embed = quit_message)
                        print('game quit')
                        return ''
                    #print('player guess: ' + player_guess.content.lower())
                    #print('check: ' + str(game.check_guess(player_guess.content.lower(), actual_word, player_turn)))
                    #print('comparison: ' + str(not game.check_guess(player_guess.content.lower(), actual_word, player_turn)))
                    # continues to retrieve a guess until a valid guess is given
                    while not game.check_guess(player_guess.content.lower(), actual_word, player_turn, difficulty):
                        # display invalid message
                        await ctx.send(embed = invalid_message, delete_after = 5.0)
                        player_guess = await bot.wait_for("message", timeout = 60.0, check = check)
                    # delete the player's guess
                    await player_guess.delete()
                    # check if the guess matches the actual word
                    if game.check_for_win(player_turn) == 'player':
                        game_status = 'player'
                        in_progress = False
                else:
                    # ai turn
                    # randomize a delay
                    random_delay = random.uniform(2.15, 3.0)
                    #print('delay: ' + str(random_delay))
                    time.sleep(random_delay)
                    start_time = time.perf_counter()
                    # retrieve guess using the corresponding difficulty
                    ai_guess = game.get_word_difficulty_extreme(player_turn, actual_word)
                    # continues to retrieve a guess until a valid guess is given
                    while not game.check_guess(ai_guess, actual_word, player_turn, difficulty):
                        ai_guess = game.get_word_difficulty_extreme(player_turn, actual_word)
                    finish_time = time.perf_counter()
                    print(str(player_turn) + ' : operation took : ' + '{:.4f}'.format(finish_time - start_time))
                    #print(game.get_black_tiles())
                    # check if the guess matches the actual word
                    if game.check_for_win(player_turn) == 'ai':
                        game_status = 'ai'
                        in_progress = False
                # continue to next turn
                player_turn += 1
                await base_game_message.edit(game.display_game_grid(player_turn, game_status, timeout, player_name, difficulty))
            # time out after player inactivity
            except asyncio.TimeoutError:
                in_progress = False
                timeout = True
                timeout_message = discord.Embed(
                    title = 'Timed Out Due to Player Inactivity',
                    color = discord.Color.from_rgb(59,136,195)
                )
                timeout_message.set_footer(text = f"{player_name_footer}")
                await ctx.send(embed = timeout_message)
    # normal and hard will have 6 rows
    else:
        while in_progress and player_turn < 13:
            try:
                # TODO: implement turn based
                # turns - player is odd, ai is even
                if player_turn % 2 != 0:
                    # player turn
                    player_guess = await bot.wait_for("message", timeout = 60.0, check = check)
                    if player_guess.content.lower() == 'quit':
                        quit_message = discord.Embed(
                            title = 'HAHAHA Quitting because YOU SUCK!?!?! >:)',
                            color = discord.Color.from_rgb(59,136,195)
                        )
                        quit_message.set_footer(text = f"{player_name_footer}")
                        await ctx.send(embed = quit_message)
                        print('game quit')
                        return ''
                    #print('player guess: ' + player_guess.content.lower())
                    #print('check: ' + str(game.check_guess(player_guess.content.lower(), actual_word, player_turn)))
                    #print('comparison: ' + str(not game.check_guess(player_guess.content.lower(), actual_word, player_turn)))
                    # continues to retrieve a guess until a valid guess is given
                    while not game.check_guess(player_guess.content.lower(), actual_word, player_turn, difficulty):
                        # display invalid message
                        await ctx.send(embed = invalid_message, delete_after = 5.0)
                        player_guess = await bot.wait_for("message", timeout = 60.0, check = check)
                    # delete the player's guess
                    await player_guess.delete()
                    # check if the guess matches the actual word
                    if game.check_for_win(player_turn) == 'player':
                        game_status = 'player'
                        in_progress = False
                else:
                    # ai turn
                    # randomize a delay
                    random_delay = random.uniform(2.15, 3.0)
                    #print('delay: ' + str(random_delay))
                    time.sleep(random_delay)
                    # determine ai difficulty
                    if difficulty == 'normal':
                        start_time = time.perf_counter()
                        # retrieve guess using the corresponding difficulty
                        ai_guess = game.get_word_difficulty_normal(player_turn)
                        # continues to retrieve a guess until a valid guess is given
                        while not game.check_guess(ai_guess, actual_word, player_turn, difficulty):
                            ai_guess = game.get_word_difficulty_normal(player_turn)
                        finish_time = time.perf_counter()
                        print(str(player_turn) + ' : operation took : ' + '{:.4f}'.format(finish_time - start_time))
                    elif difficulty == 'hard':
                        start_time = time.perf_counter()
                        # retrieve guess using the corresponding difficulty
                        ai_guess = game.get_word_difficulty_hard(player_turn)
                        # continues to retrieve a guess until a valid guess is given
                        while not game.check_guess(ai_guess, actual_word, player_turn, difficulty):
                            ai_guess = game.get_word_difficulty_hard(player_turn)
                        finish_time = time.perf_counter()
                        print(str(player_turn) + ' : operation took : ' + '{:.4f}'.format(finish_time - start_time))
                        #print(game.get_black_tiles())
                    # check if the guess matches the actual word
                    if game.check_for_win(player_turn) == 'ai':
                        game_status = 'ai'
                        in_progress = False
                # continue to next turn
                player_turn += 1
                await base_game_message.edit(game.display_game_grid(player_turn, game_status, timeout, player_name, difficulty))
            # time out after player inactivity
            except asyncio.TimeoutError:
                in_progress = False
                timeout = True
                timeout_message = discord.Embed(
                    title = 'Timed Out Due to Player Inactivity',
                    color = discord.Color.from_rgb(59,136,195)
                )
                timeout_message.set_footer(text = f"{player_name_footer}")
                await ctx.send(embed = timeout_message)
    print('game completed')
    # game completed
    # display end messages - actual word and winner/draw
    if timeout == False:
        # show winner/loser/draw end message
        if game_status == 'player':
            await ctx.send('👤 🏆')
        elif game_status == 'ai':
            await ctx.send('🤖 🏆')
        else:
            await ctx.send('👤 🤝 🤖')
        # show the actual word after match ends
        await ctx.send('correct word: ' + '||' + actual_word + '||')
    else:
        await base_game_message.edit(game.display_game_grid(player_turn, game_status, timeout, player_name, difficulty))

@bot.slash_command(guild_ids = server_id_list, description = "how-to-play Wordle")
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
                           # add statements about the ai difficulty modes
                        ),
            color = discord.Color.from_rgb(59,136,195)
        )
    help_message.set_footer(text = f"{ctx.user.name}#{ctx.user.discriminator}")

    await ctx.respond(embed = help_message)

@bot.slash_command(guild_ids = server_id_list, description = "test command")
@commands.max_concurrency(number = 1, per = commands.BucketType.user, wait = False)
async def test(ctx, difficulty: Option(str, 'normal, hard, extreme', choices = ['normal', 'hard', 'extreme'], required = True)):
    # test command
    game = WordleClass()
    print('player turn:')
    game.check_guess("lipid", "drink", 1, difficulty) # ⬛⬛⬛🟨🟨
    base_game_message = await ctx.respond(game.display_game_grid(1, 'draw', False, 'testing', difficulty))
    print('ai turn:')
    game.check_guess("sheep", "elect", 2, difficulty) # ⬛⬛🟩🟨⬛
    await base_game_message.edit(game.display_game_grid(2, 'draw', False, 'testing', difficulty))

token = open("token.txt", "r")
bot.run(token.read())