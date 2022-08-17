import random

class WordleClass:
    def __init__(self):
        with open('five-letter-words.txt','r') as words:
            self.five_letter_words = words.read().splitlines()
        self.player_grid = [
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '],
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '],
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '],
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '],
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' '],
            ['⬛', '⬛', '⬛', '⬛', '⬛', ' ']
        ]
        self.ai_grid = [
            ['⬛', '⬛', '⬛', '⬛', '⬛'],
            ['⬛', '⬛', '⬛', '⬛', '⬛'],
            ['⬛', '⬛', '⬛', '⬛', '⬛'],
            ['⬛', '⬛', '⬛', '⬛', '⬛'],
            ['⬛', '⬛', '⬛', '⬛', '⬛'],
            ['⬛', '⬛', '⬛', '⬛', '⬛']
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

    def check_guess(self):
        # TODO: check if the guess matches the correct word and returns a list containing the color indicators
        pass
