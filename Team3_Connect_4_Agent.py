# IMPORTS
import random
import copy
import math
MAX_SPACE_TO_WIN = 3
ROWS = 0
COLS = 0
MY_SYMBOL = None
OPPONENT_SYMBOL = None


# Helper: print the board (for debugging or optional use)
def print_board(board):
    """ Prints the connect 4 game board."""
    
    for row in board:
        print('|' + '|'.join(row) + '|')
    print("-" * (len(board[0]) * 2 + 1))
    print(' ' + ' '.join(str(i+1) for i in range(len(board[0]))))
    return



# FUNCTIONS REQUIRED BY THE connect_4_main.py MODULE
def init_agent(player_symbol, board_num_rows, board_num_cols, board):

   global ROWS, COLS, MY_SYMBOL, OPPONENT_SYMBOL
   num_rows = int(board_num_rows)
   num_cols = int(board_num_cols)
   ROWS = num_rows
   COLS = num_cols
   game_board = board
   MY_SYMBOL = player_symbol
   OPPONENT_SYMBOL = 'X' if player_symbol == 'O' else 'O'
   return True


# --- Helper Functions ---
def drop_disc(board, col, symbol):
    for row in reversed(range(ROWS)):
        if board[row][col] == ' ':
            board[row][col] = symbol
            return row
    return -1

def undo_disc(board, row, col):
    board[row][col] = ' '

def is_win(board, symbol):
    for r in range(ROWS):
        for c in range(COLS - MAX_SPACE_TO_WIN):
            if all(board[r][c+i] == symbol for i in range(4)): return True
    for c in range(COLS):
        for r in range(ROWS - MAX_SPACE_TO_WIN):
            if all(board[r+i][c] == symbol for i in range(4)): return True
    for r in range(ROWS - MAX_SPACE_TO_WIN):
        for c in range(COLS - MAX_SPACE_TO_WIN):
            if all(board[r+i][c+i] == symbol for i in range(4)): return True
        for c in range(MAX_SPACE_TO_WIN, COLS):
            if all(board[r+i][c-i] == symbol for i in range(4)): return True
    return False

def evaluate_move(adjacency_moves, me, opp):
    score = 0
    if adjacency_moves.count(me) == 4: score += 100
    elif adjacency_moves.count(me) == 3 and adjacency_moves.count(' ') == 1: score += 5
    elif adjacency_moves.count(me) == 2 and adjacency_moves.count(' ') == 2: score += 2
    if adjacency_moves.count(opp) == 3 and adjacency_moves.count(' ') == 1: score -= 4
    return score

def evaluate_board(board, me, opp):
    score = 0
    center = COLS // 2
    score += sum(board[r][center] == me for r in range(ROWS)) * MAX_SPACE_TO_WIN
    for r in range(ROWS):
        for c in range(COLS - MAX_SPACE_TO_WIN):
            score += evaluate_move([board[r][c+i] for i in range(4)], me, opp)
    for c in range(COLS):
        for r in range(ROWS - MAX_SPACE_TO_WIN):
            score += evaluate_move([board[r+i][c] for i in range(4)], me, opp)
    for r in range(ROWS - MAX_SPACE_TO_WIN):
        for c in range(COLS - MAX_SPACE_TO_WIN):
            score += evaluate_move([board[r+i][c+i] for i in range(4)], me, opp)
        for c in range(MAX_SPACE_TO_WIN, COLS):
            score += evaluate_move([board[r+i][c-i] for i in range(4)], me, opp)
    return score

def minimax(board, depth, alpha, beta, maximizing, me, opp):
    valid_moves = [c for c in range(COLS) if board[0][c] == ' ']
    terminal = is_win(board, me) or is_win(board, opp) or not valid_moves
    if depth == 0 or terminal:
        if is_win(board, me): return (None, math.inf)
        if is_win(board, opp): return (None, -math.inf)
        return (None, evaluate_board(board, me, opp))
    if maximizing:
        value = -math.inf
        best_col = random.choice(valid_moves)
        for col in valid_moves:
            row = drop_disc(board, col, me)
            _, score = minimax(board, depth - 1, alpha, beta, False, me, opp)
            undo_disc(board, row, col)
            if score > value:
                value = score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta: break
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_moves)
        for col in valid_moves:
            row = drop_disc(board, col, opp)
            _, score = minimax(board, depth - 1, alpha, beta, True, me, opp)
            undo_disc(board, row, col)
            if score < value:
                value = score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta: break
        return best_col, value

# ===== Main Move Function =====
def what_is_your_move(board, game_rows, game_cols, my_symbol):
    opp_symbol = 'O' if my_symbol == 'X' else 'X'
    for col in range(game_cols):
        if board[0][col] != ' ': continue
        row = drop_disc(board, col, my_symbol)
        if is_win(board, my_symbol):
            undo_disc(board, row, col)
            return col + 1
        undo_disc(board, row, col)
    for col in range(game_cols):
        if board[0][col] != ' ': continue
        row = drop_disc(board, col, opp_symbol)
        if is_win(board, opp_symbol):
            undo_disc(board, row, col)
            return col + 1
        undo_disc(board, row, col)
    best_col, _ = minimax(board, 4, -math.inf, math.inf, True, my_symbol, opp_symbol)
    return best_col + 1 if best_col is not None else 1
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
   print("Team3_Connect_4_Agent.py  is intended to be imported and not executed.") 
else:
   print("Team3_Connect_4_Agent.py  has been imported.")
