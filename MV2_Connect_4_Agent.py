#agent M

#open source code:
# https://github.com/bryanjsanchez/ConnectFour/tree/master
# AI Course Project Document from Temple University (https://cis.temple.edu/~pwang/5603-AI/Project/2021S/Sawwan/AI%20Project.pdf)


# IMPORTS
import random
import math

# DEFINITIONS
# board = [[' ' for _ in range(cols)] for _ in range(rows)]

# Global variables to store information between function calls
opponent_symbol = None
max_depth = 5  # How many moves ahead to look


# HELPER FUNCTIONS
# Print the Board
def print_board(board):
    """ Prints the connect 4 game board."""
    for row in board:
        print('|' + '|'.join(row) + '|')
    print("-" * (len(board[0]) * 2 + 1))
    print(' ' + ' '.join(str(i + 1) for i in range(len(board[0]))))
    return


def is_valid_move(board, col):
    """ Make sure column is not full. """
    return board[0][col] == ' '


def get_valid_locations(board):
    """Return a list of columns where a move can be made."""
    valid_locations = []
    for col in range(len(board[0])):
        if is_valid_move(board, col):
            valid_locations.append(col)
    return valid_locations


def get_next_open_row(board, col):
    """Find the next open row in the given column."""
    for row in range(len(board) - 1, -1, -1):
        if board[row][col] == ' ':
            return row
    return -1


def make_move(board, row, col, symbol):
    """Place a symbol at the given position."""
    board_copy = [row[:] for row in board]
    board_copy[row][col] = symbol
    return board_copy


def check_win(board, symbol):
    """Check if the given symbol has won."""
    # Check horizontal
    for row in range(len(board)):
        for col in range(len(board[0]) - 3):
            if (board[row][col] == symbol and
                    board[row][col + 1] == symbol and
                    board[row][col + 2] == symbol and
                    board[row][col + 3] == symbol):
                return True

    # Check vertical
    for row in range(len(board) - 3):
        for col in range(len(board[0])):
            if (board[row][col] == symbol and
                    board[row + 1][col] == symbol and
                    board[row + 2][col] == symbol and
                    board[row + 3][col] == symbol):
                return True

    # Check diagonal (up-right)
    for row in range(len(board) - 3):
        for col in range(len(board[0]) - 3):
            if (board[row][col] == symbol and
                    board[row + 1][col + 1] == symbol and
                    board[row + 2][col + 2] == symbol and
                    board[row + 3][col + 3] == symbol):
                return True

    # Check diagonal (up-left)
    for row in range(len(board) - 3):
        for col in range(3, len(board[0])):
            if (board[row][col] == symbol and
                    board[row + 1][col - 1] == symbol and
                    board[row + 2][col - 2] == symbol and
                    board[row + 3][col - 3] == symbol):
                return True

    return False


def evaluate_window(window, symbol):
    """Score a window of 4 positions."""
    opponent = opponent_symbol

    # Count pieces
    symbol_count = window.count(symbol)
    opponent_count = window.count(opponent)
    empty_count = window.count(' ')

    # Scoring strategy
    if symbol_count == 4:
        return 100  # Winning position
    elif symbol_count == 3 and empty_count == 1:
        return 5  # Good position
    elif symbol_count == 2 and empty_count == 2:
        return 2  # Potential position

    # Defensive scoring
    if opponent_count == 3 and empty_count == 1:
        return -80  # Opponent close to winning

    return 0


def evaluate_board(board, symbol):
    """Evaluate the entire board from perspective of the given symbol."""
    score = 0

    # Score center column (preferred control)
    center_col = len(board[0]) // 2
    center_count = 0
    for row in range(len(board)):
        if board[row][center_col] == symbol:
            center_count += 1
    score += center_count * 3

    # Score horizontal windows
    for row in range(len(board)):
        for col in range(len(board[0]) - 3):
            window = [board[row][col + i] for i in range(4)]
            score += evaluate_window(window, symbol)

    # Score vertical windows
    for row in range(len(board) - 3):
        for col in range(len(board[0])):
            window = [board[row + i][col] for i in range(4)]
            score += evaluate_window(window, symbol)

    # Score diagonal (up-right) windows
    for row in range(len(board) - 3):
        for col in range(len(board[0]) - 3):
            window = [board[row + i][col + i] for i in range(4)]
            score += evaluate_window(window, symbol)

    # Score diagonal (up-left) windows
    for row in range(len(board) - 3):
        for col in range(3, len(board[0])):
            window = [board[row + i][col - i] for i in range(4)]
            score += evaluate_window(window, symbol)

    return score


def is_terminal_node(board):
    """Check if the board is in a terminal state (win or full)."""
    return (check_win(board, 'X') or
            check_win(board, 'O') or
            len(get_valid_locations(board)) == 0)


def minimax(board, depth, alpha, beta, maximizing_player, symbol):
    """
    Minimax algorithm with alpha-beta pruning.
    Returns (best_score, best_column)
    """
    opponent = opponent_symbol
    valid_locations = get_valid_locations(board)

    # Check for terminal nodes
    if depth == 0 or is_terminal_node(board):
        if is_terminal_node(board):
            if check_win(board, symbol):
                return (10000, None)  # Our win
            elif check_win(board, opponent):
                return (-10000, None)  # Opponent win
            else:
                return (0, None)  # Draw
        else:
            return (evaluate_board(board, symbol), None)

    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            new_board = make_move(board, row, col, symbol)
            new_score, _ = minimax(new_board, depth - 1, alpha, beta, False, symbol)
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return (value, column)
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            new_board = make_move(board, row, col, opponent)
            new_score, _ = minimax(new_board, depth - 1, alpha, beta, True, symbol)
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return (value, column)


# FUNCTIONS REQUIRED BY THE connect_4_main.py MODULE
def init_agent(player_symbol, board_num_rows, board_num_cols, board):
    """ Inits the agent. Should only need to be called once at the start of a game."""
    global opponent_symbol

    # Set the opponent's symbol
    if player_symbol == 'X':
        opponent_symbol = 'O'
    else:
        opponent_symbol = 'X'

    # Adjust depth based on board size for performance
    global max_depth
    if board_num_rows * board_num_cols > 42:  # Larger than standard Connect 4
        max_depth = 4
    elif board_num_rows * board_num_cols < 42:  # Smaller than standard Connect 4
        max_depth = 6

    return True


def what_is_your_move(board, game_rows, game_cols, my_game_symbol):
    """ Decide your move, i.e., which column to drop a disk. """
    # Convert 1-indexed to 0-indexed for internal representation
    _, best_col = minimax(board, max_depth, -math.inf, math.inf, True, my_game_symbol)

    # If for some reason minimax fails, fall back to a random valid move
    if best_col is None:
        valid_moves = get_valid_locations(board)
        if valid_moves:
            best_col = random.choice(valid_moves)
        else:
            best_col = random.randint(0, game_cols - 1)

    # Convert back to 1-indexed for the game system
    return best_col + 1


def connect_4_result(board, winner, looser):
    """The Connect 4 manager calls this function when the game is over."""
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

    return True


# MAKE SURE MODULE IS IMPORTED
if __name__ == "__main__":
    print("Team1_Connect_4_Agent.py is intended to be imported and not executed.")
else:
    print("Team1_Connect_4_Agent.py has been imported.")