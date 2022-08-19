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
            ['⬛', '⬛', '⬛', '⬛', '⬛'], # 2
            ['⬛', '⬛', '⬛', '⬛', '⬛'], # 4
            ['⬛', '⬛', '⬛', '⬛', '⬛'], # 6
            ['⬛', '⬛', '⬛', '⬛', '⬛'], # 8
            ['⬛', '⬛', '⬛', '⬛', '⬛'], # 10
            ['⬛', '⬛', '⬛', '⬛', '⬛']  # 12
        ]

    def display_game_grid(self, player_turn):
        # TODO: combine player and AI grid as one message

        # TODO: build AI grid
        # player turn
        if player_turn % 2 != 0:
            str_game_grid = '🤖' + '\n'
        # AI turn
        else:
            str_game_grid = '➡️ ' + '🤖' + '\n'

        for list in self.ai_grid:
            for element in list:
                str_game_grid += element
            str_game_grid += '\n'

        # TODO: build player grid
        # player turn
        if player_turn % 2 != 0:
            str_game_grid += '\n' + '➡️ ' + '👤' + '\n'
        # AI turn
        else:
            str_game_grid += '\n' + '👤' + '\n'
        
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
        # pseudocode:
        # if guess is valid word do
        #     for each letter in guess do
        #         if the letter is in actual_word do
        #             for each letter in actual_word do
        #                 if the letter in guess is the letter in actual_word do
        #                     if the spot of the letter in guess is the same in actual_word do
        #                         make tile green
        #                         end search
        #                     else:
        #                         make tile yellow
        #                         end search
        #         else if on last letter of guess:
        #             return false
        #     return true
        # else:
        #     return false

        dictionary = enchant.Dict("en_US")
        # checks if the guess is a valid word
        if dictionary.check(guess.lower()):
            # if yes then begins search
            for guess_index, letter in enumerate(guess.lower()):
                # checks if the current letter in guess is in the actual word
                if letter in actual_word:
                    # if yes then begins to search for the letter in the actual word
                    for actual_word_index, letter in enumerate(actual_word):
                        # checks if the letter in guess matches the letter in the actual word
                        if guess[guess_index] == letter:
                            # checks if both letters are in the same spot in the word
                            if guess_index == actual_word_index:
                                print(guess[guess_index] + " : " + letter)
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
                                break
                            # otherwise it's not in the same spot
                            else:
                                print(guess[guess_index] + " : " + letter)
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
                                break
                # checks if it's the last letter - meaning no letters in guess was in the actual word
                elif guess_index == len(guess) - 1:
                    return False
            return True
        else:
            return False
