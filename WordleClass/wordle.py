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
        # TODO: build player grid
        if player_turn % 2 != 0:
            # player turn
            str_game_grid = '➡️ ' + 'player' + '\n'
        else:
            # ai turn
            str_game_grid = 'player' + '\n'
        
        for list in self.player_grid:
            for element in list:
                str_game_grid += element
            str_game_grid += '\n'
        
        # TODO: build AI grid
        if player_turn % 2 != 0:
            # player turn
            str_game_grid += '\n' + 'AI' + '\n'
        else:
            # ai turn
            str_game_grid += '\n' + '➡️ ' + 'AI' + '\n'

        for list in self.ai_grid:
            for element in list:
                str_game_grid += element
            str_game_grid += '\n'

        return str_game_grid

    def get_random_word(self):
        # randomly picks a word from the 5-letter word txt file
        return random.choice(self.five_letter_words)

    def check_guess(self):
        # TODO: check if the guess matches the correct word and returns a list containing the color indicators
        pass
