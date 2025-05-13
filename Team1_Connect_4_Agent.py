#! /usr/bin/Team1_Connect_4_Agent.py 
# IMPORTS
import random

# DEFINITIONS
# board = [[' ' for _ in range(cols)] for _ in range(rows)]

# HELPER FUNCTIONS
# Print the Board

MAX_SPACE_TO_WIN = 3


ROWS = None
COLS = None
MY_SYMBOL = None
OPPONENT_SYMBOL = None



def print_board(board):
    """ Prints the connect 4 game board."""
    for row in board:
        print('|' + '|'.join(row) + '|')
    print("-" * (len(board[0]) * 2 + 1))
    print(' ' + ' '.join(str(i+1) for i in range(len(board[0]))))
    return



# FUNCTIONS REQUIRED BY THE connect_4_main.py MODULE
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
   global ROWS, COLS, MY_SYMBOL, OPPONENT_SYMBOL
   num_rows = int(board_num_rows)
   num_cols = int(board_num_cols)
   ROWS = num_rows
   COLS = num_cols
   game_board = board
   MY_SYMBOL = player_symbol
   OPPONENT_SYMBOL = 'X' if player_symbol == 'O' else 'O'
   return True




def available_cols(board):
    """ Returns a list of available columns to drop a disk. """
    available = []
    for col in range(COLS):
        if board[0][col] == ' ':
            available.append(col)
    return available


def is_terminal_board(board):
    """ Check if the board is full or if there is a winner. """
    if detect_win(board, MY_SYMBOL):
        return (True, MY_SYMBOL)
    elif detect_win(board, OPPONENT_SYMBOL):
        return (True, OPPONENT_SYMBOL)
    elif len(available_cols(board)) == 0:
        return (True, None)
    return (False, None)


def detect_win(board, player):
    """ Check if the player has a winning move. """

    # Check horizontal win
    for col in range(COLS - MAX_SPACE_TO_WIN):
        for row in range(ROWS):
            if board[row][col] == player and board[row][col + 1] == player and board[row][col + 2] == player and board[row][col + 3] == player:
                return True
    
    # Check vertical win
    for col in range(COLS):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            if board[row][col] == player and board[row + 1][col] == player and board[row + 2][col] == player and board[row + 3][col] == player:
                return True
    
    # Check diagonal win (bottom-left to top-right)
    for col in range(COLS - MAX_SPACE_TO_WIN):
        for row in range(MAX_SPACE_TO_WIN, ROWS):
            if board[row][col] == player and board[row - 1][col + 1] == player and board[row - 2][col + 2] == player and board[row - 3][col + 3] == player:
                return True

    # Check diagonal win (top-left to bottom-right)
    for col in range(COLS - MAX_SPACE_TO_WIN):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            if board[row][col] == player and board[row + 1][col + 1] == player and board[row + 2][col + 2] == player and board[row + 3][col + 3] == player:
                return True
    return False

def score(board, player):
    """ Calculate the score of the board for the given player. """
    score = 0

    # Give more weight to MAX_SPACE_TO_WIN in the center of the board
    center_col = COLS // 2
    for row in range(ROWS):
        if board[row][center_col] == player:
            score += 3

    for offset in range(0,MAX_SPACE_TO_WIN + 1, 2):
        for row in range(ROWS):
            left_col = center_col - offset
            right_col = center_col + offset
            if left_col >= 0 and board[row][left_col] == player:
                score += 2
            if right_col < len(board[0]) and board[row][right_col] == player:
                score += 2
    



    # Check horizontal
    for col in range(COLS - MAX_SPACE_TO_WIN):
        for row in range(ROWS):
            adjacent_pieces = [board[row][col + i] for i in range(MAX_SPACE_TO_WIN + 1)]
            score += evaluate_window(adjacent_pieces, player)
    
    # Check vertical
    for col in range(COLS):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            adjacent_pieces = [board[row + i][col] for i in range(MAX_SPACE_TO_WIN + 1)]
            score += evaluate_window(adjacent_pieces, player)
    
    # Check diagonal (bottom-left to top-right)
    for col in range(COLS - MAX_SPACE_TO_WIN):
        for row in range(MAX_SPACE_TO_WIN, ROWS):
            adjacent_pieces = [board[row - i][col + i] for i in range(MAX_SPACE_TO_WIN + 1)]
            score += evaluate_window(adjacent_pieces, player)
    
    # Check diagonal (top-left to bottom-right)
    for col in range(COLS - MAX_SPACE_TO_WIN):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            adjacent_pieces = [board[row + i][col + i] for i in range(MAX_SPACE_TO_WIN)]
            score += evaluate_window(adjacent_pieces, player)
    return score

def evaluate_window(adjacent_pieces, player):
    opponent = OPPONENT_SYMBOL if player == MY_SYMBOL else MY_SYMBOL
    score = 0
    player_pieces = 0
    empty_spaces = 0
    opponent_pieces = 0
    for p in adjacent_pieces:
        if p == player:
            player_pieces += 1
        elif p == opponent:
            opponent_pieces += 1
        else:
            empty_spaces += 1
    if player_pieces == 4:
        score += 99999
    elif player_pieces == 3 and empty_spaces == 1:
        score += 100
    elif player_pieces == 2 and empty_spaces == 2:
        score += 10
    return score 

def clone_and_place_piece(board, player, column):
    new_board = board.copy()
    place_piece(new_board, player, column)
    return new_board

def place_piece(board, player, column):
    index = column
    for row in reversed(range(ROWS)):
        if board[row][index] == ' ':
            board[row][index] = player
            return

def minimax(board, depth, alpha, beta, maximizing_player):
    """ Minimax algorithm with alpha-beta pruning. """

    # Get the available columns
    available = available_cols(board)

    # Check if the game is over or if we reached the maximum depth
    is_terminal, winner = is_terminal_board(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winner == MY_SYMBOL: # Winner is AI
                return (None,1000000)
            elif winner == OPPONENT_SYMBOL: # Winner is Player
                return (None,-1000000)
            else: # Tie
                return (None, 0)
        else: # Depth is 0
            return (None, score(board, MY_SYMBOL))
    
    # If the game is not over and we have not reached the maximum depth
    if maximizing_player:
        value = float('-inf')
        # if every choice is a tie, choose randomly
        col = random.choice(available)
        
        # expand the selected column
        for c in available:
            new_board = clone_and_place_piece(board, MY_SYMBOL, c)
            new_score = minimax(new_board, depth - 1 , alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                col = c
            # alpha-beta pruning
            if value > alpha:
                alpha = new_score
            
            # if beta is less than or equal to alpha, there will be no need to check other branches because there will not be a better move
            if beta <= alpha:
                break
        return (col, value)
    else:
        value = float('inf')
        # if every choice is a tie, choose randomly
        col = random.choice(available)
        # expand the selected column
        for c in available:
            new_board = clone_and_place_piece(board, OPPONENT_SYMBOL, c)
            new_score = minimax(new_board, depth - 1 , alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                col = c
            # alpha-beta pruning
            if value < beta:
                beta = value
            
            # if beta is less than or equal to alpha, there will be no need to check other branches because there will not be a better move
            if beta <= alpha:
                break
        return (col, value)
            



def what_is_your_move(board, game_rows, game_cols, my_game_symbol):
   """ Decide your move, i.e., which column to drop a disk. """

   # Insert your agent code HERE to decide which column to drop/insert your disk.
    global ROWS, COLS, MY_SYMBOL, OPPONENT_SYMBOL
    ROWS = int(game_rows)
    COLS = int(game_cols)
    MY_SYMBOL = my_game_symbol
    OPPONENT_SYMBOL = 'X' if my_game_symbol == 'O' else 'O'
    
    best_col, _ = minimax(board, 5, float('-inf'), float('inf'), True)
    if not best_col:
        best_col = 0
    return best_col


def connect_4_result(board, winner, looser):
    """The Connect 4 manager calls this function when the game is over.
    If there is a winner, the team name of the winner and looser are the
    values of the respective argument variables. If there is a draw/tie,
    the values of winner = looser = 'Draw'."""

    # Check if a draw
    if winner == "Draw":
        print(">>> I am player TEAM1 <<<")
        print(">>> The game resulted in a draw. <<<\n")
        return True

    print(">>> I am player TEAM1 <<<")
    print("The winner is " + winner)
    if winner == "Team1":
        print("YEAH!!  :-)")
    else:
        print("BOO HOO HOO  :~(")
    print("The looser is " + looser)
    print()

    # print("The final board is") # Uncomment if you want to print the game board.
    # print(board)  # Uncomment if you want to print the game board.

    # Insert your code HERE to do whatever you like with the arguments.

    return True


#####
# MAKE SURE MODULE IS IMPORTED
if __name__ == "__main__":
   print("Team1_Connect_4_Agent.py  is intended to be imported and not executed.") 
else:
   print("Team1_Connect_4_Agent.py  has been imported.")
