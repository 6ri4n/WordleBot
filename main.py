import asyncio
import random
import time
import discord
import aiosqlite
from discord import Option
from discord.ext import commands
from WordleClass.wordle import WordleClass

server_id_list = [872995966066757673, 999054346715156480]
bot = commands.Bot(command_prefix = ".", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print(f"\nONLINE\nLogged in as {bot.user}\n")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name = "Wordle"))
    # create table in database
    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS users
                                (userId TEXT,
                                displayName TEXT,
                                userPoints INTEGER,
                                totalWin INTEGER,
                                totalLoss INTEGER,
                                totalGame INTEGER,
                                totalDraw INTEGER,
                                totalTimeout INTEGER,
                                totalForfeit INTEGER)''')
        await db.commit()

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
    # TODO: function to interact with database
    async def db_operation(user_id, display_name, difficulty, operation):
        # check if user is in table
        async with aiosqlite.connect('database.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('''SELECT userId
                                    FROM users
                                    WHERE userId = ?''', (user_id,))
                check = await cursor.fetchone()
                if check is None:
                    # user not found
                    #print('user not found in database')
                    await cursor.execute('''INSERT INTO users
                                        (userId,
                                        displayName,
                                        userPoints,
                                        totalWin,
                                        totalLoss,
                                        totalGame,
                                        totalDraw,
                                        totalTimeout,
                                        totalForfeit)
                                        VALUES (?, ?, 0, 0, 0, 0, 0, 0, 0)''', (user_id, display_name,))
                    #print('user added to database')
                if operation == 'w':
                    # increase total win
                    await cursor.execute('''UPDATE users
                                        SET totalWin = totalWin + 1
                                        WHERE userId == ?
                                        ''', (user_id,))
                    # check for difficulty to award points
                    if difficulty == 'normal':
                        await cursor.execute('''UPDATE users
                                        SET userPoints = userPoints + 1
                                        WHERE userId == ?
                                        ''', (user_id,))
                    elif difficulty == 'hard':
                        await cursor.execute('''UPDATE users
                                        SET userPoints = userPoints + 20
                                        WHERE userId == ?
                                        ''', (user_id,))
                    elif difficulty == 'extreme':
                        await cursor.execute('''UPDATE users
                                        SET userPoints = userPoints + 75
                                        WHERE userId == ?
                                        ''', (user_id,))
                elif operation == 'l':
                    # increase total loss
                    await cursor.execute('''UPDATE users
                                        SET totalLoss = totalLoss + 1
                                        WHERE userId == ?
                                        ''', (user_id,))
                elif operation == 'd':
                    # increase total draw
                    await cursor.execute('''UPDATE users
                                        SET totalDraw = totalDraw + 1
                                        WHERE userId == ?
                                        ''', (user_id,))
                elif operation == 't':
                    # increase total timeout
                    await cursor.execute('''UPDATE users
                                        SET totalTimeout = totalTimeout + 1
                                        WHERE userId == ?
                                        ''', (user_id,))
                elif operation == 'f':
                    # increase total forfeit
                    await cursor.execute('''UPDATE users
                                        SET totalForfeit = totalForfeit + 1
                                        WHERE userId == ?
                                        ''', (user_id,))
                # increase total game
                await cursor.execute('''UPDATE users
                                        SET totalGame = totalGame + 1
                                        WHERE userId == ?
                                        ''', (user_id,))
                # check if display name for the user needs to be updated
                await cursor.execute('''SELECT displayName
                                    FROM users
                                    WHERE userId = ?''', (user_id,))
                check_display_name = await cursor.fetchone()
                if check_display_name[0] != ctx.user.name + '#' + ctx.user.discriminator:
                    display_name = ctx.user.name + '#' + ctx.user.discriminator
                    await cursor.execute('''UPDATE users
                                        SET displayName = ?
                                        WHERE userId == ?
                                        ''', (display_name, user_id,))
            await db.commit()

    # TODO: play wordle against an AI

    # randomly set a 5-letter word that the player and ai is supposed to guess
    game = WordleClass()
    actual_word = game.get_random_word()

    # player goes first
    player_turn = 1
    player_name_footer = ctx.user.name + '#' + ctx.user.discriminator
    player_name = '<@' + str(ctx.user.id) + '>'
    player_id = str(ctx.user.id)

    def check(message):
        return (message.author == ctx.author and ctx.channel.id == message.channel.id and len(message.content) == 5) or (message.author == ctx.author and ctx.channel.id == message.channel.id and message.content.lower() == 'ff')
    
    def format_incorrect_letter_message(incorrect_letter_list):
        if incorrect_letter_list == []:
            return 'incorrect letters:\n[]'
        else:
            incorrect_letter_list.sort()
            message = 'incorrect letters:\n['
            for letter in incorrect_letter_list:
                message += letter + ', '
            return message[:len(message) - 2] + ']'

    # game progress
    in_progress = True
    timeout = False
    # winner/loser/draw
    game_status = 'draw'

    #print('game start')
    #print('actual word: ' + actual_word)
    interaction_game_message = await ctx.respond(game.display_game_grid(player_turn, game_status, timeout, player_name, difficulty))
    incorrect_letter_message = await ctx.send(format_incorrect_letter_message(game.get_player_black_tiles()))
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
                    if player_guess.content.lower() == 'ff':
                        await incorrect_letter_message.edit(format_incorrect_letter_message(game.get_player_black_tiles()) + '\ncorrect word: ' + '||' + actual_word + '||')
                        await ctx.respond('HAHAHA Quitting because YOU SUCK!?!?! >:)', ephemeral = True)
                        await db_operation(player_id, player_name_footer, difficulty, 'f')
                        return ''
                    #print('player guess: ' + player_guess.content.lower())
                    #print('check: ' + str(game.check_guess(player_guess.content.lower(), actual_word, player_turn)))
                    #print('comparison: ' + str(not game.check_guess(player_guess.content.lower(), actual_word, player_turn)))
                    # continues to retrieve a guess until a valid guess is given
                    while not game.check_guess(player_guess.content.lower(), actual_word, player_turn, difficulty):
                        # display invalid message
                        await ctx.respond('Invalid Word, Please Try Again', ephemeral = True)
                        player_guess = await bot.wait_for("message", timeout = 60.0, check = check)
                        if player_guess.content.lower() == 'ff':
                            await incorrect_letter_message.edit(format_incorrect_letter_message(game.get_player_black_tiles()) + '\ncorrect word: ' + '||' + actual_word + '||')
                            await ctx.respond('HAHAHA Quitting because YOU SUCK!?!?! >:)', ephemeral = True)
                            await db_operation(player_id, player_name_footer, difficulty, 'f')
                            return ''
                    # delete the player's guess
                    await player_guess.delete()
                    # display player's incorrect letters
                    await incorrect_letter_message.edit(format_incorrect_letter_message(game.get_player_black_tiles()))
                    # check if the guess matches the actual word
                    if game.check_for_win(player_turn) == 'player':
                        game_status = 'player'
                        in_progress = False
                else:
                    # ai turn
                    # randomize a delay
                    #random_delay = random.uniform(2.15, 3.0)
                    #print('delay: ' + str(random_delay))
                    #time.sleep(random_delay)
                    start_time = time.perf_counter()
                    # retrieve guess using the corresponding difficulty
                    ai_guess = game.get_word_difficulty_extreme(player_turn, actual_word)
                    # continues to retrieve a guess until a valid guess is given
                    while not game.check_guess(ai_guess, actual_word, player_turn, difficulty):
                        ai_guess = game.get_word_difficulty_extreme(player_turn, actual_word)
                    finish_time = time.perf_counter()
                    #print('ai guess: ' + ai_guess)
                    #print(str(player_turn) + ' : operation took : ' + '{:.4f}'.format(finish_time - start_time))
                    #print(game.get_ai_black_tiles())
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
                await ctx.respond('Timed Out Due to Player Inactivity', ephemeral = True)
    # normal and hard will have 6 rows
    else:
        while in_progress and player_turn < 13:
            try:
                # TODO: implement turn based
                # turns - player is odd, ai is even
                if player_turn % 2 != 0:
                    # player turn
                    player_guess = await bot.wait_for("message", timeout = 60.0, check = check)
                    if player_guess.content.lower() == 'ff':
                        await incorrect_letter_message.edit(format_incorrect_letter_message(game.get_player_black_tiles()) + '\ncorrect word: ' + '||' + actual_word + '||')
                        await ctx.respond('HAHAHA Quitting because YOU SUCK!?!?! >:)', ephemeral = True)
                        await db_operation(player_id, player_name_footer, difficulty, 'f')
                        return ''
                    #print('player guess: ' + player_guess.content.lower())
                    #print('check: ' + str(game.check_guess(player_guess.content.lower(), actual_word, player_turn)))
                    #print('comparison: ' + str(not game.check_guess(player_guess.content.lower(), actual_word, player_turn)))
                    # continues to retrieve a guess until a valid guess is given
                    while not game.check_guess(player_guess.content.lower(), actual_word, player_turn, difficulty):
                        # display invalid message
                        await ctx.respond('Invalid Word, Please Try Again', ephemeral = True)
                        player_guess = await bot.wait_for("message", timeout = 60.0, check = check)
                        if player_guess.content.lower() == 'ff':
                            await incorrect_letter_message.edit(format_incorrect_letter_message(game.get_player_black_tiles()) + '\ncorrect word: ' + '||' + actual_word + '||')
                            await ctx.respond('HAHAHA Quitting because YOU SUCK!?!?! >:)', ephemeral = True)
                            await db_operation(player_id, player_name_footer, difficulty, 'f')
                            return ''
                    # delete the player's guess
                    await player_guess.delete()
                    # display player's incorrect letters
                    await incorrect_letter_message.edit(format_incorrect_letter_message(game.get_player_black_tiles()))
                    # check if the guess matches the actual word
                    if game.check_for_win(player_turn) == 'player':
                        game_status = 'player'
                        in_progress = False
                else:
                    # ai turn
                    # randomize a delay
                    #random_delay = random.uniform(2.15, 3.0)
                    #print('delay: ' + str(random_delay))
                    #time.sleep(random_delay)
                    # determine ai difficulty
                    if difficulty == 'normal':
                        start_time = time.perf_counter()
                        # retrieve guess using the corresponding difficulty
                        ai_guess = game.get_word_difficulty_normal(player_turn)
                        # continues to retrieve a guess until a valid guess is given
                        while not game.check_guess(ai_guess, actual_word, player_turn, difficulty):
                            ai_guess = game.get_word_difficulty_normal(player_turn)
                        finish_time = time.perf_counter()
                        #print('ai guess: ' + ai_guess)
                        #print(str(player_turn) + ' : operation took : ' + '{:.4f}'.format(finish_time - start_time))
                    elif difficulty == 'hard':
                        start_time = time.perf_counter()
                        # retrieve guess using the corresponding difficulty
                        ai_guess = game.get_word_difficulty_hard(player_turn)
                        # continues to retrieve a guess until a valid guess is given
                        while not game.check_guess(ai_guess, actual_word, player_turn, difficulty):
                            ai_guess = game.get_word_difficulty_hard(player_turn)
                        finish_time = time.perf_counter()
                        #print('ai guess: ' + ai_guess)
                        #print(str(player_turn) + ' : operation took : ' + '{:.4f}'.format(finish_time - start_time))
                        #print(game.get_ai_black_tiles())
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
                await ctx.respond('Timed Out Due to Player Inactivity', ephemeral = True)
    #print('game completed\n')
    # game completed
    # display end messages - actual word and winner/draw
    if timeout == False:
        # show winner/loser/draw end message
        if game_status == 'player':
            state = '👤 🏆'
            await db_operation(player_id, player_name_footer, difficulty, 'w')
        elif game_status == 'ai':
            state = '🤖 🏆'
            await db_operation(player_id, player_name_footer, difficulty, 'l')
        else:
            state = '👤 🤝 🤖'
            await db_operation(player_id, player_name_footer, difficulty, 'd')
        # show the actual word after match ends
        await incorrect_letter_message.edit(format_incorrect_letter_message(game.get_player_black_tiles()) + '\n' + state + ' correct word: ' + '||' + actual_word + '||')
    else:
        await base_game_message.edit(game.display_game_grid(player_turn, game_status, timeout, player_name, difficulty))
        await incorrect_letter_message.edit(format_incorrect_letter_message(game.get_player_black_tiles()) + '\ncorrect word: ' + '||' + actual_word + '||')
        await db_operation(player_id, player_name_footer, difficulty, 't')

@bot.slash_command(guild_ids = server_id_list, description = "displays a user\'s stats")
@commands.max_concurrency(number = 1, per = commands.BucketType.user, wait = False)
async def stats(ctx, user: Option(str, 'mention a user', required = False)):
    # TODO: display user stats
    # mentioning will display the mentioned user stats, otherwise display the stats of the user that ran the command
    if user is None:
        # user that ran the command
        user_id = ctx.user.id
        async with aiosqlite.connect('database.db') as db:
            async with db.cursor() as cursor:
                # check if user is in table
                await cursor.execute('''SELECT userId
                                    FROM users
                                    WHERE userId = ?''', (user_id,))
                check = await cursor.fetchone()
                if check is None:
                    # user not found
                    await ctx.respond('No Available Player Stats to Display', ephemeral = True)
                else:
                    # displayer user's stats
                    # retrieve stats
                    await cursor.execute('''SELECT userId,
                                        displayName,
                                        userPoints,
                                        totalWin,
                                        totalLoss,
                                        totalGame,
                                        totalDraw,
                                        totalTimeout,
                                        totalForfeit
                                        FROM users
                                        WHERE userId = ?''', (user_id,))
                    stats = await cursor.fetchone()
                    #print(stats)
                    point = stats[2]
                    win = stats[3]
                    loss = stats[4]
                    game = stats[5]
                    draw = stats[6]
                    timeout = stats[7]
                    forfeit = stats[8]
                    win_rate = (win / game) * 100
                    # retrieve rank stat
                    await cursor.execute('''SELECT userId
                                        FROM users
                                        ORDER BY userPoints DESC
                                        ''')
                    stats_rank = await cursor.fetchall()
                    for position, id in enumerate(stats_rank):
                        #print(id)
                        if int(id[0]) == user_id:
                            rank = position + 1
                            break
                    if rank == 1:
                        rank = '🥇'
                    elif rank == 2:
                        rank = '🥈'
                    elif rank == 3:
                        rank = '🥉'
                    #print(stats_rank)
                    # display stats of the user that ran the command
                    stats_message = discord.Embed(
                        title = 'Player Stats',
                        description = f'Player: {ctx.user.mention}\nRank: **{rank}** | **{point}** Points\nTotal: **{game}** Games\n**{win}** Wins | **{loss}** Losses | **{draw}** Draws\n**{timeout}** Timeouts | **{forfeit}** Forfeits',
                        color = discord.Color.from_rgb(59,136,195)
                    )
                    stats_message.set_footer(text = f'Win Rate: {win_rate:.2f}%')
                    await ctx.respond(embed = stats_message)
                    # check if display name for the user needs to be updated
                    if stats[1] != ctx.user.name + '#' + ctx.user.discriminator:
                        display_name = ctx.user.name + '#' + ctx.user.discriminator
                        await cursor.execute('''UPDATE users
                                            SET displayName = ?
                                            WHERE userId == ?
                                            ''', (display_name, user_id,))
            await db.commit()
    elif user[0:3] == '<@!' and user[-1] == '>':
        # mentioned user
        user_id = int(user[3:len(user) - 1])
        async with aiosqlite.connect('database.db') as db:
            async with db.cursor() as cursor:
                # check if user is in table
                await cursor.execute('''SELECT userId
                                    FROM users
                                    WHERE userId = ?''', (user_id,))
                check = await cursor.fetchone()
                if check is None:
                    # user not found
                    await ctx.respond('No Available Player Stats to Display', ephemeral = True)
                else:
                    # display mentioned user's stats
                    # retrieve stats
                    await cursor.execute('''SELECT userId,
                                        userPoints,
                                        totalWin,
                                        totalLoss,
                                        totalGame,
                                        totalDraw,
                                        totalTimeout,
                                        totalForfeit
                                        FROM users
                                        WHERE userId = ?''', (user_id,))
                    stats = await cursor.fetchone()
                    #print(stats)
                    point = stats[1]
                    win = stats[2]
                    loss = stats[3]
                    game = stats[4]
                    draw = stats[5]
                    timeout = stats[6]
                    forfeit = stats[7]
                    win_rate = (win / game) * 100
                    # retrieve rank stat
                    await cursor.execute('''SELECT userId
                                        FROM users
                                        ORDER BY userPoints DESC
                                        ''')
                    stats_rank = await cursor.fetchall()
                    for position, id in enumerate(stats_rank):
                        #print(id)
                        if int(id[0]) == user_id:
                            rank = position + 1
                            break
                    if rank == 1:
                        rank = '🥇'
                    elif rank == 2:
                        rank = '🥈'
                    elif rank == 3:
                        rank = '🥉'
                    #print(stats_rank)
                    # display stats of the user that ran the command
                    stats_message = discord.Embed(
                        title = 'Player Stats',
                        description = f'Player: <@!{user_id}>\nRank: **{rank}** | **{point}** Points\nTotal: **{game}** Games\n**{win}** Wins | **{loss}** Losses | **{draw}** Draws\n**{timeout}** Timeouts | **{forfeit}** Forfeits',
                        color = discord.Color.from_rgb(59,136,195)
                    )
                    stats_message.set_footer(text = f'Win Rate: {win_rate:.2f}%')
                    await ctx.respond(embed = stats_message)

@bot.slash_command(guild_ids = server_id_list, description = "global leaderboard")
@commands.cooldown(1, 60, commands.BucketType.user)
async def lb(ctx):
    # TODO: display the top 10 users with the highest points
    async with aiosqlite.connect('database.db') as db:
        async with db.cursor() as cursor:
            # retrieve top 10 players
            await cursor.execute('''SELECT displayName,
                                    userPoints
                                    FROM users
                                    ORDER BY userPoints DESC
                                    LIMIT 10''')
            lb = await cursor.fetchall()
            players = ''
            # build player string
            for rank, player in enumerate(lb):
                if rank == 0:
                    players += f'🥇 {player[0]} | **{player[1]}** Points\n'
                elif rank == 1:
                    players += f'🥈 {player[0]} | **{player[1]}** Points\n'
                elif rank == 2:
                    players += f'🥉 {player[0]} | **{player[1]}** Points\n'
                else:
                    players += f'**{rank + 1}**. {player[0]} | **{player[1]}** Points\n'
            lb_message = discord.Embed(
                title = 'Global Leaderboard',
                description = players,
                color = discord.Color.from_rgb(59,136,195)
            )
            lb_message.set_footer(text = 'Top 10 Players')
            await ctx.respond(embed = lb_message)

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
    help_message.add_field(name = 'Hard.', value = '20-points.', inline = True)
    help_message.add_field(name = 'Extreme.', value = '75-points.', inline = True)
    help_message.add_field(name = 'Win.', value = 'Player will be awarded with points that vary depending on the match difficulty. This will count towards the player\'s total amount of games played.', inline = True)
    help_message.add_field(name = 'Loss.', value = 'Player will not be awarded with any points. This will count towards the player\'s total amount of games played.', inline = True)
    help_message.add_field(name = 'Draw.', value = 'Player will not be awarded with any points. This will count towards the player\'s total amount of games played.', inline = True)
    help_message.add_field(name = 'Inactivity Policy.', value = 'One minute of inactivity from the player will result in the game timing out (this will count towards the player\'s total amount of games played).', inline = False)
    help_message.add_field(name = 'Q: Can I end the match early?', value = 'A: Yes, during your turn you can enter \'quit\' (without the single quotes) to end the match early (this will count towards the player\'s total amount of games played).', inline = False)
    help_message.add_field(name = 'Pro Tip:', value = 'Entering an invalid word will reset your inactivity timer.', inline = False)
    help_message.set_footer(text = ctx.user.name + '#' + ctx.user.discriminator)
    await ctx.respond(embed = help_message)

@bot.slash_command(guild_ids = server_id_list, description = "test command")
@commands.max_concurrency(number = 1, per = commands.BucketType.user, wait = False)
async def wipe(ctx, var):
    # test command
    await ctx.respond('test command', ephemeral = True)
    if ctx.user.id == 329066373743378432:
        if var[0:3] == '<@!' and var[-1] == '>':
            user_id = int(var[3:len(var) - 1])
            operation = 'user'
        elif var == 'table':
            operation = 'table'
        async with aiosqlite.connect('database.db') as db:
            async with db.cursor() as cursor:
                if operation == 'user':
                    # check if user is in table
                    await cursor.execute('''SELECT userId FROM users WHERE userId = ?''', (user_id,))
                    check = await cursor.fetchone()
                    if check is None:
                        # user not found
                        await ctx.respond('user not found', ephemeral = True)
                    else:
                        # delete user from table
                        await cursor.execute('''DELETE FROM users WHERE userId = ?''', (user_id,))
                        #print('deleted user')
                elif operation == 'table':
                    await cursor.execute('''DROP TABLE users''')
                    #print('deleted users table')
            await db.commit()

@bot.slash_command(guild_ids = server_id_list, description = "test command")
@commands.max_concurrency(number = 1, per = commands.BucketType.user, wait = False)
async def guess(ctx, guess: Option(str, 'enter guess', required = True), word: Option(str, 'enter correct word', required = True)):
    game = WordleClass()
    player_turn = 1
    game_status = 'draw'
    timeout = False
    player_name = 'test'
    difficulty = 'normal'
    guess = guess
    actual_word = word
    base = await ctx.respond(game.display_game_grid(player_turn, game_status, timeout, player_name, difficulty))
    game_message = await base.original_message()
    game.check_guess(guess, actual_word, player_turn, difficulty)
    await game_message.edit(game.display_game_grid(player_turn, game_status, timeout, player_name, difficulty))
    await ctx.send('correct word: ' + actual_word)

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)