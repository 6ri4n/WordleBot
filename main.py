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
        await ctx.respond(embed = invalid_message, ephemeral = True)
    elif isinstance(error, commands.MaxConcurrencyReached):
        invalid_message = discord.Embed(
            title = 'Please Finish Your Current Game',
            color = discord.Color.from_rgb(59,136,195)
        )
        invalid_message.set_footer(text = f"{player_name_footer}")
        await ctx.respond(embed = invalid_message, ephemeral = True)
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
        return (message.author == ctx.author and ctx.channel.id == message.channel.id and len(message.content) == 5) or (message.author == ctx.author and ctx.channel.id == message.channel.id and message.content.lower() == 'quit')
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
    print('game completed\n')
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
            title = 'HOW TO PLAY',
            description = 'Guess the correct five letter word within six attempts (four attempts at extreme difficulty).',
            color = discord.Color.from_rgb(59,136,195)
        )
    help_message.add_field(name = 'Each guess must be a valid five letter word within the English dictionary.', value = 'During your turn (indicated with ➡️) enter your guess (as a message) in the same channel to submit.', inline = False)
    help_message.add_field(name = 'After each guess, the color of the tiles will change to indicate how close your guess was to the correct word.', value = 'Green tile indicates that the letter is in the word and in the correct spot.\nYellow tile indicates that the letter is in the word but in the wrong spot.\nBlack tile indicates that the letter is not in the word.', inline = False)
    help_message.add_field(name = 'Examples.', value = 'correct word:\n:regional_indicator_d: :regional_indicator_r: :regional_indicator_i: :regional_indicator_n: :regional_indicator_k:\n\nguesses:\n:regional_indicator_c: :regional_indicator_u: :regional_indicator_p: :regional_indicator_i: :regional_indicator_d:\n⬛ ⬛ ⬛ 🟨 🟨\n\n:regional_indicator_t: :regional_indicator_r: :regional_indicator_a: :regional_indicator_i: :regional_indicator_t:\n⬛ 🟩 ⬛ 🟨 ⬛\n\nPoint System:', inline = False)
    help_message.add_field(name = 'Normal.', value = '1-point.', inline = True)
    help_message.add_field(name = 'Hard.', value = '3-points.', inline = True)
    help_message.add_field(name = 'Extreme.', value = '15-points.', inline = True)
    help_message.add_field(name = 'Win.', value = 'Player will be awarded with points that vary depending on the match difficulty. This will count towards the player\'s total amount of games played.', inline = True)
    help_message.add_field(name = 'Loss.', value = 'Player will not be awarded with any points. This will count towards the player\'s total amount of games played.', inline = True)
    help_message.add_field(name = 'Draw.', value = 'Player will not be awarded with any points. This will count towards the player\'s total amount of games played.', inline = True)
    help_message.add_field(name = 'Inactivity Policy.', value = 'One minute of inactivity from the player will result in the game timing out (this will count towards the player\'s total amount of games played).', inline = False)
    help_message.add_field(name = 'Q: Can I end the match early?', value = 'A: Yes, enter \'quit\' (without the single quotes) to end the match early (this will count towards the player\'s total amount of games played).', inline = False)
    help_message.set_footer(text = f"{ctx.user.name}#{ctx.user.discriminator}")
    await ctx.respond(embed = help_message)

@bot.slash_command(guild_ids = server_id_list, description = "test command")
@commands.max_concurrency(number = 1, per = commands.BucketType.user, wait = False)
async def test(ctx, difficulty: Option(str, 'normal, hard, extreme', choices = ['normal', 'hard', 'extreme'], required = True)):
    # test command
    await ctx.respond('test command', ephemeral = True)
    game = WordleClass()
    #print('player turn:')
    game.check_guess("cupid", "drink", 1, difficulty) # ⬛⬛⬛🟨🟨
    base_game_message = await ctx.send(game.display_game_grid(1, 'draw', False, 'testing', difficulty))
    #print('ai turn:')
    game.check_guess("trait", "drink", 2, difficulty) # ⬛🟩⬛🟨⬛
    await base_game_message.edit(game.display_game_grid(2, 'draw', False, 'testing', difficulty))

token = open("token.txt", "r")
bot.run(token.read())