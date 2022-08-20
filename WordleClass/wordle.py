import random
import enchant

class WordleClass:
    def __init__(self):
        with open('five-letter-words.txt','r') as words:
            self.five_letter_words = words.read().splitlines()
        self.player_grid = [
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '], # 1
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '], # 3
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '], # 5
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '], # 7
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '], # 9
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' ']  # 11
        ]
        self.ai_grid = [
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '], # 2
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '], # 4
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '], # 6
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '], # 8
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '], # 10
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' ']  # 12
        ]

    def display_game_grid(self, player_turn, game_status, timeout):
        # TODO: combine player and ai grid as one message
        # check for win condition or timeout or last turn to display proper ending grid
        if game_status == 'player' or game_status == 'ai' or timeout == True or player_turn == 13:
            # TODO: build ai grid first and then player grid second
            # set first line to have no arrow emote
            str_game_grid = '🤖' + '\n'
            # build ai grid
            for list in self.ai_grid:
                for element in list:
                    str_game_grid += element
                str_game_grid += '\n'
            # set first line to have no arrow emote
            str_game_grid += '\n' + '👤' + '\n'
            # build player grid
            for list in self.player_grid:
                for element in list:
                    str_game_grid += element
                str_game_grid += '\n'
        else:
            # TODO: build ai grid first and then player grid second
            # determine whose turn
            if player_turn % 2 != 0:
                # player turn so no arrow emote on ai
                str_game_grid = '🤖' + '\n'
            else:
                # ai turn so no arrow emote on player
                str_game_grid = '➡️ ' + '🤖' + '\n'
            # build ai grid
            for list in self.ai_grid:
                for element in list:
                    str_game_grid += element
                str_game_grid += '\n'
            # determine whose turn
            if player_turn % 2 != 0:
                # player turn so set arrow emote
                str_game_grid += '\n' + '➡️ ' + '👤' + '\n'
            else:
                # ai turn so no arrow emote on player
                str_game_grid += '\n' + '👤' + '\n'
            # build player grid
            for list in self.player_grid:
                for element in list:
                    str_game_grid += element
                str_game_grid += '\n'
        # finished grid message
        return str_game_grid

    def get_random_word(self):
        # randomly picks a word from the 5-letter word txt file
        return random.choice(self.five_letter_words)

    def check_guess(self, guess, actual_word, player_turn):
        # TODO:
        # check if the guess is a valid word from the dictionary
        # check if the guess has any matches to the correct word
        # returns a boolean
        #
        # algorithm:
        # guess - horse, actual word - hence
        # letters in guess start large search in actual word then gradually decreases the amount of search
        # the letter h in horse would search the letters in actual word: h, e, n, c, e
        # the letter o in horse would search the letters in actual word: e, n, c, e
        # the letter r in horse would search the letters in actual word: n, c, e
        # the letter s in horse would search the letters in actual word: c, e
        # the letter e in horse would search the letters in actual word: e
        #
        # pseudocode:
        # if guess is valid word do
        #     for each letter in guess do
        #         if letter is in actual_word do
        #             guess_letter_in_actual_word += 1
        #     if guess_letter_in_actual_word > 0:
        #         for each letter in actual_word do
        #             if the letter in guess == the letter in actual_word do
        #                 if the spot of the letter in guess is the same in actual_word do
        #                     make tile green
        #                     end search
        #                 else:
        #                     make tile yellow
        #                     end search
        #                 reduce the search in actual word
        #                 break
        #             reduce the search in actual word
        #     else:
        #         return false
        #     return true
        # else:
        #     return false

        dictionary = enchant.Dict('en_US')
        #print('guess: ' + guess)
        #print('word in dictionary: ' + str(dictionary.check(guess)))
        # checks if the guess is a valid word
        if dictionary.check(guess):
            # check to see if any letters in guess match the actual word
            guess_letter_in_actual_word = 0
            for guess_letter in guess:
                if guess_letter in actual_word:
                    guess_letter_in_actual_word += 1
            # check if there are any matches, if it's greater than 0 then there are matches
            if guess_letter_in_actual_word > 0 :
                # begin to search for matches
                for guess_index, guess_letter in enumerate(guess):
                    # checks if the current letter in guess is in the actual word - decreases search each iteration
                    if guess_letter in actual_word:
                        # if yes then begins to search for the letter in the actual word
                        for actual_word_letter in actual_word:
                            # checks if the letter in guess matches the letter in the actual word
                            if guess_letter == actual_word_letter:
                                # determine index of the letter from the actual word
                                # because the search in actual word gets reduced each iteration
                                if len(actual_word) == 1:
                                    actual_word_index = 4
                                elif len(actual_word) == 2:
                                    actual_word_index = 3
                                elif len(actual_word) == 3:
                                    actual_word_index = 2
                                elif len(actual_word) == 4:
                                    actual_word_index = 1
                                else:
                                    actual_word_index = 0

                                if guess_index == actual_word_index:
                                    #print('match: ' + str(guess_index) + ' : ' + str(actual_word_index))
                                    # make tile green
                                    # check whose turn it is
                                    if player_turn % 2 != 0:
                                        # player turn
                                        # turn // 2 gives the row of the list, guess_index gives the column of the list
                                        self.player_grid[int(player_turn // 2)][guess_index] = '🟩'
                                    else:
                                        # ai turn
                                        # (turn / 2) - 1 gives the row of the list, guess_index gives the column of the list
                                        self.ai_grid[int((player_turn / 2) -1)][guess_index] = '🟩'
                                # otherwise it's not in the same spot
                                else:
                                    #print('!! no match: ' + str(guess_index) + ' : ' + str(actual_word_index))
                                    # make tile yellow
                                    # check whose turn it is
                                    if player_turn % 2 != 0:
                                        # player turn
                                        # turn // 2 gives the row of the list, guess_index gives the column of the list
                                        self.player_grid[int(player_turn // 2)][guess_index] = '🟨'
                                    else:
                                        # ai turn
                                        # (turn / 2) - 1 gives the row of the list, guess_index gives the column of the list
                                        self.ai_grid[int((player_turn / 2) -1)][guess_index] = '🟨'
                                # ends current letter to move onto next letter in the search
                                actual_word = actual_word[1:]
                                #print(actual_word)
                                break
                            # continue to limit the search
                            actual_word = actual_word[1:]
                            #print(actual_word)
                    else:
                        # continue to limit the search
                        actual_word = actual_word[1:]
                        #print(actual_word)
                # check whose turn it is
                if player_turn % 2 != 0:
                    # display guess on player turn
                    self.player_grid[int(player_turn // 2)][5] = ' ' + guess
                    print('turn ' + str(int(player_turn // 2) + 1) + ' - player guess: ' + guess)
                else:
                    # display guess on ai turn
                    self.ai_grid[int((player_turn / 2) -1)][5] = ' ' + guess
                    print('turn ' + str(int((player_turn / 2) -1) + 1) + ' - ai guess: ' + guess)
                return True
            else:
                # check whose turn it is
                if player_turn % 2 != 0:
                    # display guess on player turn
                    self.player_grid[int(player_turn // 2)][5] = ' ' + guess
                    print('turn ' + str(int(player_turn // 2) + 1) + ' - player guess: ' + guess)
                else:
                    # display guess on ai turn
                    self.ai_grid[int((player_turn / 2) -1)][5] = ' ' + guess
                    print('turn ' + str(int((player_turn / 2) -1) + 1) + ' - ai guess: ' + guess)
                return True
        else:
            # invalid word
            return False

    def check_for_win(self, player_turn):
        # TODO: check for win condition
        if player_turn % 2 != 0:
            # player turn
            # check if the guess is all green - guess matches the actual word
            if self.player_grid[int(player_turn // 2)][:5] == ['🟩', '🟩', '🟩', '🟩', '🟩']:
                return 'player'
        else:
            # ai turn
            if self.ai_grid[int((player_turn / 2) -1)][:5] == ['🟩', '🟩', '🟩', '🟩', '🟩']:
                return 'ai'

    def get_word_difficulty_test(self):
        # difficulty test - 
        # randomly picks a word from the 5-letter word txt file
        return random.choice(self.five_letter_words)

    