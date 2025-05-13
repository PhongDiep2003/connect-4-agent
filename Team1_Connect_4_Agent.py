#! /usr/bin/Team1_Connect_4_Agent.py

# IMPORTS
import random
import math

# DEFINITIONS / REPRESENTATION LOGIC
# (Board is a 2D list of characters. ' ' = empty, 'X' and 'O' = player pieces.)

# HELPER FUNCTIONS – Representation and basic game logic
def print_board(board):
    """Contributors: Team1 Member1 (50%), Team1 Member2 (50%)
    Prints the Connect 4 game board to the console for debugging or visualization."""
    for row in board:
        print('|' + '|'.join(row) + '|')
    print("-" * (len(board[0]) * 2 + 1))
    print(' ' + ' '.join(str(i+1) for i in range(len(board[0]))))
    return

def drop_piece(board, col, symbol):
    """Contributors: Team1 Member1 (50%), Team1 Member2 (50%)
    Representation Logic: Drops a piece with the given symbol into the specified column.
    The piece will occupy the lowest available row in that column.
    Returns the row index where the piece lands, or -1 if the column is full."""
    rows = len(board)
    for r in range(rows-1, -1, -1):  # start from bottom row
        if board[r][col] == ' ':
            board[r][col] = symbol
            return r
    return -1  # column is full

def undo_piece(board, row, col):
    """Contributors: Team1 Member1 (50%), Team1 Member2 (50%)
    Representation Logic: Removes a piece from the board at the given (row, col) position.
    This effectively undoes a move, restoring that cell to empty."""
    board[row][col] = ' '
    return

def is_win_for(board, symbol):
    """Contributors: Team1 Member1 (50%), Team1 Member2 (50%)
    Representation/Reasoning Logic: Checks if the given symbol has four in a row on the board.
    Scans horizontally, vertically, and both diagonal directions for a win."""
    rows = len(board)
    cols = len(board[0])
    # Check horizontal wins
    for r in range(rows):
        for c in range(cols - 3):
            if board[r][c] == symbol and board[r][c+1] == symbol and board[r][c+2] == symbol and board[r][c+3] == symbol:
                return True
    # Check vertical wins
    for c in range(cols):
        for r in range(rows - 3):
            if board[r][c] == symbol and board[r+1][c] == symbol and board[r+2][c] == symbol and board[r+3][c] == symbol:
                return True
    # Check diagonal (down-right) wins
    for r in range(rows - 3):
        for c in range(cols - 3):
            if board[r][c] == symbol and board[r+1][c+1] == symbol and board[r+2][c+2] == symbol and board[r+3][c+3] == symbol:
                return True
    # Check diagonal (down-left) wins
    for r in range(rows - 3):
        for c in range(3, cols):
            if board[r][c] == symbol and board[r+1][c-1] == symbol and board[r+2][c-2] == symbol and board[r+3][c-3] == symbol:
                return True
    return False

# REASONING LOGIC – Heuristic evaluation of board states
def evaluate_window(window, my_symbol, opp_symbol):
    """Contributors: Team1 Member1 (50%), Team1 Member2 (50%)
    Reasoning Logic: Scores a window of four cells for the heuristic evaluation.
    Awards points for windows that are favorable to my_symbol and penalizes ones favorable to opp_symbol."""
    score = 0
    # Favorable patterns for my_symbol
    if window.count(my_symbol) == 4:
        score += 100  # Winning window (4 in a row for me)
    elif window.count(my_symbol) == 3 and window.count(' ') == 1:
        score += 5    # Three of mine and one empty (one move to win)
    elif window.count(my_symbol) == 2 and window.count(' ') == 2:
        score += 2    # Two of mine and two empties
    # Unfavorable patterns (opponent)
    if window.count(opp_symbol) == 3 and window.count(' ') == 1:
        score -= 4    # Three of opponent's and one empty (one move for opponent to win)
    return score

def evaluate_board(board, my_symbol, opp_symbol):
    """Contributors: Team1 Member1 (50%), Team1 Member2 (50%)
    Reasoning Logic: Heuristic evaluation function for the board state from the perspective of my_symbol.
    Returns a numeric score where higher is better for my_symbol."""
    rows = len(board)
    cols = len(board[0])
    score = 0

    # 1. Center control heuristic – prioritize owning the center column (and adjacent if even number of columns)
    center_col = cols // 2
    center_count = 0
    if cols % 2 == 1:
        # odd number of columns: single center column
        for r in range(rows):
            if board[r][center_col] == my_symbol:
                center_count += 1
    else:
        # even number of columns: consider both central columns
        center_left = center_col - 1
        for r in range(rows):
            if board[r][center_col] == my_symbol or board[r][center_left] == my_symbol:
                center_count += 1
    score += center_count * 3  # each center piece gets a moderate bonus

    # 2. Evaluate all possible 4-length windows on the board
    # Horizontal windows
    for r in range(rows):
        for c in range(cols - 3):
            window = [board[r][c+i] for i in range(4)]
            score += evaluate_window(window, my_symbol, opp_symbol)
    # Vertical windows
    for c in range(cols):
        for r in range(rows - 3):
            window = [board[r+i][c] for i in range(4)]
            score += evaluate_window(window, my_symbol, opp_symbol)
    # Down-right diagonal windows
    for r in range(rows - 3):
        for c in range(cols - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, my_symbol, opp_symbol)
    # Down-left diagonal windows
    for r in range(rows - 3):
        for c in range(3, cols):
            window = [board[r+i][c-i] for i in range(4)]
            score += evaluate_window(window, my_symbol, opp_symbol)

    return score

# SEARCH LOGIC – Minimax with Alpha-Beta Pruning
def alpha_beta_search(board, depth, alpha, beta, maximizing_player, my_symbol, opp_symbol):
    """Contributors: Team1 Member1 (50%), Team1 Member2 (50%)
    Search Logic: Minimax algorithm with Alpha-Beta pruning.
    Recursively evaluates moves up to a given depth and returns the heuristic score of the board.
    Uses alpha (best score for maximizer so far) and beta (best for minimizer) to prune branches."""
    # Get list of valid moves (columns that are not full)
    valid_moves = [c for c in range(len(board[0])) if board[0][c] == ' ']
    # Check terminal conditions
    is_terminal = is_win_for(board, my_symbol) or is_win_for(board, opp_symbol) or (len(valid_moves) == 0)
    if depth == 0 or is_terminal:
        # If at depth limit or game over, return evaluated score
        if is_terminal:
            # If game over, return a very large positive/negative/zero score
            if is_win_for(board, my_symbol):
                return math.inf    # my_symbol has won
            elif is_win_for(board, opp_symbol):
                return -math.inf   # opponent has won
            else:
                return 0           # no moves left (draw)
        else:
            # Depth limit reached, return heuristic evaluation
            return evaluate_board(board, my_symbol, opp_symbol)

    # Recursive search with alpha-beta pruning
    if maximizing_player:
        max_eval = -math.inf
        for col in valid_moves:
            # simulate dropping my piece
            row = drop_piece(board, col, my_symbol)
            eval_score = alpha_beta_search(board, depth - 1, alpha, beta, False, my_symbol, opp_symbol)
            # undo move
            undo_piece(board, row, col)
            # update the max evaluation
            if eval_score > max_eval:
                max_eval = eval_score
            alpha = max(alpha, max_eval)
            if alpha >= beta:
                break  # prune branch
        return max_eval
    else:
        min_eval = math.inf
        for col in valid_moves:
            # simulate dropping opponent's piece
            row = drop_piece(board, col, opp_symbol)
            eval_score = alpha_beta_search(board, depth - 1, alpha, beta, True, my_symbol, opp_symbol)
            # undo move
            undo_piece(board, row, col)
            # update the min evaluation
            if eval_score < min_eval:
                min_eval = eval_score
            beta = min(beta, min_eval)
            if alpha >= beta:
                break  # prune branch
        return min_eval

# FUNCTIONS REQUIRED BY connect_4_main.py

def init_agent(player_symbol, board_num_rows, board_num_cols, board):
    """Contributors: Team1 Member1 (50%), Team1 Member2 (50%)
    Initializes the agent at the start of a game. This function could set up any necessary state.
    In this implementation, we simply ensure the game parameters are noted."""
    # Note: All necessary parameters are passed in each call, so we don't store state between turns.
    num_rows = int(board_num_rows)
    num_cols = int(board_num_cols)
    game_board = board
    my_game_symbol = player_symbol
    # Determine opponent's symbol for completeness (not stored globally due to stateless design)
    if player_symbol == 'X':
        opponent_symbol = 'O'
    else:
        opponent_symbol = 'X'
    # (No persistent state is kept; return True to indicate successful initialization)
    return True

def what_is_your_move(board, game_rows, game_cols, my_game_symbol):
    """Contributors: Team1 Member1 (50%), Team1 Member2 (50%)
    Decide and return the next move (column number) for the agent.
    Applies rule-based reasoning for immediate wins/blocks, then uses Alpha-Beta search for the best move.
    Returns a column index in 1..game_cols (inclusive) to drop a disk."""
    # Identify opponent's symbol for reasoning
    opponent_symbol = 'O' if my_game_symbol == 'X' else 'X'

    # REASONING: Rule-based immediate win check
    # If we can win in this move, do it.
    for col in range(game_cols):
        if board[0][col] != ' ':
            continue  # skip if column is full
        row = drop_piece(board, col, my_game_symbol)
        if row != -1 and is_win_for(board, my_game_symbol):
            # Undo the simulation and return this winning move immediately
            undo_piece(board, row, col)
            return col + 1  # return 1-indexed column
        undo_piece(board, row, col)

    # REASONING: Rule-based block opponent's win
    # If the opponent can win next turn, block them by playing that column.
    for col in range(game_cols):
        if board[0][col] != ' ':
            continue
        row = drop_piece(board, col, opponent_symbol)
        if row != -1 and is_win_for(board, opponent_symbol):
            # This column is a winning move for the opponent, so we must block it.
            undo_piece(board, row, col)
            return col + 1
        undo_piece(board, row, col)

    # SEARCH: Use Minimax (Alpha-Beta) to choose the best move if no immediate win/block is found
    best_score = -math.inf
    best_col = None
    # We can optionally randomize the order of columns to explore to vary moves in symmetric situations
    columns = [c for c in range(game_cols) if board[0][c] == ' ']
    # (No sorting is done here, but could sort by center proximity for move ordering optimization)
    for col in columns:
        # simulate dropping our piece in this column
        row = drop_piece(board, col, my_game_symbol)
        # search one less depth (because we made one move) as minimizing player next
        score = alpha_beta_search(board, depth=4, alpha=-math.inf, beta=math.inf,
                                  maximizing_player=False, my_symbol=my_game_symbol, opp_symbol=opponent_symbol)
        # undo the move
        undo_piece(board, row, col)
        # choose the move with the highest score
        if score > best_score:
            best_score = score
            best_col = col

    # If for some reason no move was chosen (shouldn't happen unless board is full),
    # pick a random valid column.
    if best_col is None:
        best_col = random.choice(columns) if columns else 0

    return best_col + 1  # return as 1-indexed column number

# Ensure the module is imported properly and not executed directly
if __name__ == "__main__":
    print("Team1_Connect_4_Agent.py is intended to be imported and not executed.")
else:
    print("Team1_Connect_4_Agent.py has been imported.")

