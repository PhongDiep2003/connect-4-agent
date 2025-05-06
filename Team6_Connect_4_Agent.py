#! /usr/bin/Team6_Connect_4_Agent.py

# IMPORTS
import random

# DEFINITIONS
# board = [[' ' for _ in range(cols)] for _ in range(rows)]

# HELPER FUNCTIONS
# Print the Board
def print_board(board):
    """ Prints the connect 4 game board."""
    for row in board:
        print('|' + '|'.join(row) + '|')
    print("-" * (len(board[0]) * 2 + 1))
    print(' ' + ' '.join(str(i+1) for i in range(len(board[0]))))


def init_agent(player_symbol, board_num_rows, board_num_cols, board):
    """ Inits the agent. Should only need to be called once at the start of a game.
    NOTE NOTE NOTE: Do not expect the values you might save in variables to retain
    their values each time a function in this module is called. Therefore, you might
    want to save the variables to a file and re-read them when each function was called.
    This is not to say you should do that. Rather, just letting you know about the variables
    you might use in this module.
    NOTE NOTE NOTE NOTE: All functions called by connect_4_main.py  module will pass in all
    of the variables that you likely will need. So you can probably skip the 'NOTE NOTE NOTE'
    above. """
    num_rows = int(board_num_rows)
    num_cols = int(board_num_cols)
    game_board = board
    my_game_symbol = player_symbol
    return True

def what_is_your_move(board, game_rows, game_cols, my_game_symbol):
   """ Decide your move, i.e., which column to drop a disk. """

   valid_columns = []
   for col in range(game_cols):
       if board[0][col] == ' ':  # Check if top cell is empty
           valid_columns.append(col + 1)  # +1 for 1-based indexing
   if not valid_columns:
       return 1  # fallback
   return random.choice(valid_columns)

#####
# MAKE SURE MODULE IS IMPORTED
if __name__ == "__main__":
   print("Team6_Connect_4_Agent.py  is intended to be imported and not executed.")
else:
   print("Team6_Connect_4_Agent.py  has been imported.")
