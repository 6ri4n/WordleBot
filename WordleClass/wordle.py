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

    def check_guess(self, guess, word, player_turn):
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
        print(str(player_turn) + ' : ' + str(guess))
        # checks if the guess is a valid word
        if dictionary.check(guess):
            # check whose turn it is
            if player_turn % 2 != 0:
                # display guess on player turn
                self.player_grid[int(player_turn // 2)][5] = ' ' + guess
            else:
                # display guess on ai turn
                self.ai_grid[int((player_turn / 2) -1)][5] = ' ' + guess
            # check to see if any letters in guess match the actual word
            guess_letter_in_actual_word = 0
            actual_word = word
            for guess_letter in guess:
                if guess_letter in actual_word:
                    guess_letter_in_actual_word += 1
            # check if there are any matches, if it's greater than 0 then there are matches
            if guess_letter_in_actual_word > 0 :
                # begin to search for matches
                for guess_index, guess_letter in enumerate(guess):
                    print(guess_letter + ' : ' + str(actual_word) + ' : ' + str(guess_letter in actual_word))
                    # checks if the current letter in guess is in the actual word
                    if guess_letter in actual_word:
                        # if yes then begins to search for the letter in the actual word
                        for actual_word_letter in actual_word:
                            # checks if the letter in guess matches the letter in the actual word
                            print('comparing: ' + guess_letter + ' : ' + actual_word_letter + ' - searching in: ' + actual_word)
                            if guess_letter == actual_word_letter:
                                # determine index of the letter from the actual word
                                # because the search in actual word gets reduced each iteration
                                actual_word_index = word.index(guess_letter, guess_index)
                                print('guess index: ' + str(guess_index) + ' - actual word index: ' + str(actual_word_index))
                                if guess_index == actual_word_index:
                                    print('match: ' + str(guess_index) + ' : ' + str(actual_word_index))
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
                                    print('!! no match: ' + str(guess_index) + ' : ' + str(actual_word_index))
                                    # check if there are any of the same guess letters in the rest of the actual word 
                                    # if there are then leave the current tile black
                                    print(guess_letter + ' count in ' + guess[guess_index:] + ' : ' + str(guess[guess_index:].count(guess_letter)))
                                    print(guess[guess_index:].count(guess_letter) > 1 and guess[guess_index:].count(guess_letter) > actual_word.count(actual_word_letter))
                                    if guess[guess_index:].count(guess_letter) > 1 and guess[guess_index:].count(guess_letter) > actual_word.count(actual_word_letter):
                                        print('duplicate letter: ' + guess_letter)
                                        # continue to limit the search
                                        actual_word = actual_word[1:]
                                        break
                                    else:
                                        # otherwise make tile yellow
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
                                # continue to limit the search
                                actual_word = actual_word[1:]
                                break
                    else:
                        # guess letter not in actual word - continue to limit the search
                        actual_word = actual_word[1:]
                        print('letter not in actual word')
                return True
            else:
                # valid guess but no matches
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

    def get_word_difficulty_easy(self):
        # TODO: difficulty test - generates guess that takes into account of yellow tiles
        return random.choice(self.five_letter_words)

    def get_word_difficulty_normal(self, actual_word, player_turn):
        # TODO: difficulty easy - generates guess that takes into account of green and yellow tiles
        if player_turn == 2:
            return random.choice(self.five_letter_words)
        # check if there are any green tiles from previous guess
        elif '🟩' in self.ai_grid[int((player_turn / 2) -1) - 1]:
            # generate guess with the correct letters from the previous guess
            generate_complete = False
            while not generate_complete:
                green_tiles = 0
                letter_matches = 0
                ai_guess = random.choice(self.five_letter_words)
                if ai_guess == self.ai_grid[int((player_turn / 2) -1)][5][1:]:
                    break
                # searches for the green tiles from previous guess
                for previous_guess_index, tile in enumerate(self.ai_grid[int((player_turn / 2) -1) - 1]):
                    if tile == '🟩':
                        green_tiles += 1
                        for current_guess_index, letter in enumerate(ai_guess):
                            if letter == self.ai_grid[int((player_turn / 2) -1) - 1][5][previous_guess_index + 1] and previous_guess_index == current_guess_index:
                                letter_matches += 1
                if letter_matches == green_tiles:
                    generate_complete = True
            return ai_guess
        # otherwise generate random guess
        else:
            return random.choice(self.five_letter_words)

    def get_word_difficulty_hard(self):
        # TODO: difficulty normal - generates guess that takes into account of green, yellow, and black tiles
        pass

