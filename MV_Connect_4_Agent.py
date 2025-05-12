#! /usr/bin/MV_Connect_4_Agent.py

# IMPORTS
import random
import math

# DEFINITIONS
# Global variables
EMPTY = ' '
MAX_DEPTH = 12  # Increased depth since there are no constraints
# Standard Connect 4 board dimensions
ROWS = 6
COLS = 7
# Transposition table for caching evaluated positions
position_cache = {}


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
    """Check if a move is valid (column is not full)."""
    return board[0][col] == EMPTY


def get_valid_moves(board, cols):
    """Returns list of valid columns to place a piece."""
    valid_moves = []
    for col in range(cols):
        if is_valid_move(board, col):
            valid_moves.append(col)
    return valid_moves


def make_move(board, col, player, rows):
    """Place a piece in the specified column."""
    # Create a deep copy of the board
    new_board = [row[:] for row in board]

    # Find the lowest empty cell in the column
    for row in range(rows - 1, -1, -1):
        if new_board[row][col] == EMPTY:
            new_board[row][col] = player
            return new_board, row

    # This should never happen if is_valid_move is called first
    return None, None


def check_winner(board, row, col, player, rows, cols):
    """Check if the last move resulted in a win."""
    # Define the four directions to check: horizontal, vertical, diagonal /,  diagonal \
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for dr, dc in directions:
        count = 1  # Count the player's pieces in the current direction

        # Check in the positive direction
        r, c = row + dr, col + dc
        while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
            count += 1
            r += dr
            c += dc

        # Check in the negative direction
        r, c = row - dr, col - dc
        while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc

        # If 4 or more in a row, the player wins
        if count >= 4:
            return True

    return False


def is_board_full(board, cols):
    """Check if the board is full (draw)."""
    return all(board[0][col] != EMPTY for col in range(cols))


def evaluate_window(window, player, opponent):
    """Score a window of 4 positions."""
    score = 0
    player_count = window.count(player)
    opponent_count = window.count(opponent)
    empty_count = window.count(EMPTY)

    # No mixed pieces - either all player's, opponent's, or empty
    if player_count > 0 and opponent_count == 0:
        # Exponential scoring for player's pieces
        if player_count == 4:
            score += 1000000  # Winning position - extremely high score
        elif player_count == 3 and empty_count == 1:
            score += 5000  # One move away from winning
        elif player_count == 2 and empty_count == 2:
            score += 500  # Two moves away, but still a threat
        elif player_count == 1 and empty_count == 3:
            score += 100  # Beginning of a potential line

    # Opponent's pieces - we need to defend
    if opponent_count > 0 and player_count == 0:
        if opponent_count == 3 and empty_count == 1:
            score -= 50000  # Critical - opponent one move away from winning
        elif opponent_count == 2 and empty_count == 2:
            score -= 500  # Opponent building a threat
        elif opponent_count == 1 and empty_count == 3:
            score -= 100  # Opponent starting a potential line

    return score


def evaluate_board(board, player, opponent, rows, cols):
    """Evaluate the board state for the given player."""
    score = 0

    # Score center column - control of center is crucial in Connect 4
    center_col = cols // 2
    center_count = sum(1 for row in range(rows) if board[row][center_col] == player)
    score += center_count * 5  # Increased weight for center control

    # For standard Connect 4, prioritize lower positions (closer to base)
    for col in range(cols):
        for row in range(rows):
            if board[row][col] == player:
                # More points for pieces lower in the columns
                score += 0.2 * (rows - row)  # Increased weight

    # Threat-based scoring system (core evaluation logic)
    # Score horizontal windows
    for row in range(rows):
        for col in range(cols - 3):
            window = [board[row][col + i] for i in range(4)]
            score += evaluate_window(window, player, opponent)

    # Score vertical windows
    for col in range(cols):
        for row in range(rows - 3):
            window = [board[row + i][col] for i in range(4)]
            score += evaluate_window(window, player, opponent)

    # Score diagonal (positive slope) windows
    for row in range(rows - 3):
        for col in range(cols - 3):
            window = [board[row + i][col + i] for i in range(4)]
            score += evaluate_window(window, player, opponent)

    # Score diagonal (negative slope) windows
    for row in range(3, rows):
        for col in range(cols - 3):
            window = [board[row - i][col + i] for i in range(4)]
            score += evaluate_window(window, player, opponent)

    # Evaluate connected pieces (adjacent pieces) which increase threat potential
    for row in range(rows):
        for col in range(cols):
            if board[row][col] == player:
                # Check 8 surrounding positions for connected pieces
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == player:
                            score += 0.5  # Bonus for connected pieces

    # Evaluate control of key strategic positions
    if rows == 6 and cols == 7:  # Standard Connect 4 board
        # These positions have been identified as strategically valuable
        key_positions = [
            (5, 2), (5, 3), (5, 4),  # Bottom center positions
            (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),  # One row up, wider span
            (3, 2), (3, 3), (3, 4)  # Two rows up, center positions
        ]

        for row, col in key_positions:
            if board[row][col] == player:
                score += 1.0  # Increased bonus for controlling key positions
            elif board[row][col] == opponent:
                score -= 1.0  # Increased penalty if opponent controls them

    # Evaluate mobility (available future moves)
    # Having more valid moves above your pieces is generally advantageous
    player_mobility = 0
    opponent_mobility = 0

    for col in range(cols):
        # Find the topmost piece in each column
        for row in range(rows):
            if board[row][col] != EMPTY:
                if row > 0:  # If the column is not full
                    if board[row][col] == player:
                        player_mobility += 1
                    elif board[row][col] == opponent:
                        opponent_mobility += 1
                break

    # Reward having more mobility than opponent
    score += 0.3 * (player_mobility - opponent_mobility)

    return score


def minimax(board, depth, alpha, beta, maximizing_player, player, opponent, rows, cols):
    """
    Minimax algorithm with alpha-beta pruning to find the best move.
    Returns a tuple of (score, column) where column is the best move.
    """
    # Create a unique key for the current board state to use for caching
    board_key = ''.join(''.join(row) for row in board) + str(depth) + str(maximizing_player)

    # Check if we've already evaluated this position
    if board_key in position_cache:
        return position_cache[board_key]

    valid_moves = get_valid_moves(board, cols)

    # Check if game is over (win/loss/draw)
    is_win = False
    win_player = None

    # Check for wins
    for col in range(cols):
        for row in range(rows):
            if board[row][col] != EMPTY:
                # Check if the last move resulted in a win
                if check_winner(board, row, col, board[row][col], rows, cols):
                    is_win = True
                    win_player = board[row][col]
                    break
        if is_win:
            break

    # Return score for terminal states
    if is_win:
        if win_player == player:
            return 1000000 + depth, None  # Player win (prefer quicker wins)
        else:
            return -1000000 - depth, None  # Opponent win (prefer delaying losses)

    # Check for draw
    if len(valid_moves) == 0:
        return 0, None  # Draw

    # If we've reached max depth, evaluate the board
    if depth == 0:
        score = evaluate_board(board, player, opponent, rows, cols)
        position_cache[board_key] = (score, None)
        return score, None

    # Order moves to improve alpha-beta efficiency
    ordered_moves = order_moves(board, valid_moves, player, opponent, rows, cols, maximizing_player)

    if maximizing_player:
        value = -math.inf
        column = ordered_moves[0] if ordered_moves else valid_moves[0]  # Default to first move

        # Try each valid move in our ordered list
        for col in ordered_moves:
            new_board, row = make_move(board, col, player, rows)

            # Check if this move results in a win
            if row is not None and check_winner(new_board, row, col, player, rows, cols):
                position_cache[board_key] = (1000000 + depth, col)
                return 1000000 + depth, col  # Return a high value for winning move

            # Recursive call to minimax
            new_score, _ = minimax(new_board, depth - 1, alpha, beta, False, player, opponent, rows, cols)

            # Handle equal scores by slightly favoring center columns
            if new_score == value:
                # Prefer center columns when scores are equal
                if abs(col - cols // 2) < abs(column - cols // 2):
                    column = col
            # Update the best move if better score found
            elif new_score > value:
                value = new_score
                column = col

            # Alpha-beta pruning
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cutoff

        # Store result in cache before returning
        position_cache[board_key] = (value, column)
        return value, column
    else:
        value = math.inf
        column = ordered_moves[0] if ordered_moves else valid_moves[0]  # Default to first move

        # Try each valid move in our ordered list
        for col in ordered_moves:
            new_board, row = make_move(board, col, opponent, rows)

            # Check if this move results in a win for opponent
            if row is not None and check_winner(new_board, row, col, opponent, rows, cols):
                position_cache[board_key] = (-1000000 - depth, col)
                return -1000000 - depth, col  # Return a low value for opponent winning move

            # Recursive call to minimax
            new_score, _ = minimax(new_board, depth - 1, alpha, beta, True, player, opponent, rows, cols)

            # Handle equal scores by slightly favoring center columns
            if new_score == value:
                # Prefer center columns when scores are equal
                if abs(col - cols // 2) < abs(column - cols // 2):
                    column = col
            # Update the best move if better score found
            elif new_score < value:
                value = new_score
                column = col

            # Alpha-beta pruning
            beta = min(beta, value)
            if alpha >= beta:
                break  # Alpha cutoff

        # Store result in cache before returning
        position_cache[board_key] = (value, column)
        return value, column


def order_moves(board, valid_moves, player, opponent, rows, cols, maximizing_player):
    """
    Order moves for alpha-beta pruning efficiency.
    Returns valid_moves in an order that is likely to produce cutoffs early.
    """
    # Create a list of (score, column) pairs
    move_scores = []

    # Current player
    current_player = player if maximizing_player else opponent

    # 1. Check for immediate winning moves
    for col in valid_moves:
        new_board, row = make_move(board, col, current_player, rows)

        # If this move wins, put it first
        if row is not None and check_winner(new_board, row, col, current_player, rows, cols):
            return [col] + [c for c in valid_moves if c != col]

    # 2. Evaluate each move with a quick heuristic
    for col in valid_moves:
        # Make the move
        new_board, row = make_move(board, col, current_player, rows)
        if row is None:
            continue

        # Calculate a simple score for this move
        score = 0

        # Prefer center columns
        score -= abs(col - cols // 2) * 2

        # Check if this move creates threats
        # Horizontal threat check
        for c in range(max(0, col - 3), min(cols - 3, col + 1)):
            window = [new_board[row][c + i] for i in range(4)]
            if window.count(current_player) == 3 and window.count(EMPTY) == 1:
                score += 100

        # Vertical threat check
        if row <= rows - 4:
            window = [new_board[row + i][col] for i in range(4)]
            if window.count(current_player) == 3 and window.count(EMPTY) == 1:
                score += 100

        # Diagonal threats
        # Positive slope
        for r, c in zip(range(max(0, row - 3), min(rows - 3, row + 1)),
                        range(max(0, col - 3), min(cols - 3, col + 1))):
            if 0 <= r < rows - 3 and 0 <= c < cols - 3:
                window = [new_board[r + i][c + i] for i in range(4)]
                if window.count(current_player) == 3 and window.count(EMPTY) == 1:
                    score += 100

        # Negative slope
        for r, c in zip(range(min(rows - 1, row + 3), max(3, row - 1), -1),
                        range(max(0, col - 3), min(cols - 3, col + 1))):
            if 3 <= r < rows and 0 <= c < cols - 3:
                window = [new_board[r - i][c + i] for i in range(4)]
                if window.count(current_player) == 3 and window.count(EMPTY) == 1:
                    score += 100

        move_scores.append((score, col))

    # Sort by score (descending for maximizing player, ascending for minimizing)
    if maximizing_player:
        move_scores.sort(reverse=True)
    else:
        move_scores.sort()

    # Return just the columns in the right order
    return [col for _, col in move_scores]


# Cache for storing previously computed positions
position_cache = {}


def get_best_move(board, player, opponent, rows, cols):
    """Get the best move using minimax with alpha-beta pruning."""
    # With no depth constraints, we can do a complete search for endgame positions
    empty_cells = sum(row.count(EMPTY) for row in board)

    # For the opening moves, use established opening theory
    if empty_cells >= (ROWS * COLS) - 2:  # First or second move
        # Center column is optimal for first move
        center_col = COLS // 2
        if is_valid_move(board, center_col):
            return center_col
        # If center is taken, choose an adjacent column
        if is_valid_move(board, center_col - 1):
            return center_col - 1
        if is_valid_move(board, center_col + 1):
            return center_col + 1

    # Check for immediate winning moves first
    for col in range(cols):
        if is_valid_move(board, col):
            new_board, row = make_move(board, col, player, rows)
            if row is not None and check_winner(new_board, row, col, player, rows, cols):
                return col  # Found a winning move, no need for minimax

    # Check for opponent winning moves to block
    for col in range(cols):
        if is_valid_move(board, col):
            new_board, row = make_move(board, col, opponent, rows)
            if row is not None and check_winner(new_board, row, col, opponent, rows, cols):
                return col  # Found a move to block opponent's win

    # For endgame, we can search deeper or even do a complete search
    # The number of empty cells is a good indicator of how deep we can search
    if empty_cells <= 10:
        # Near endgame, do a deeper search
        depth = min(empty_cells, MAX_DEPTH)
    elif empty_cells <= 20:
        depth = min(10, MAX_DEPTH)
    else:
        # Early to mid-game, use standard depth
        depth = 8

    # Clear cache if it gets too large
    global position_cache
    if len(position_cache) > 10000000:  # Increased cache size
        position_cache.clear()

    # Initialize alpha and beta values for pruning
    alpha = -math.inf
    beta = math.inf

    # Get the best move column using minimax search
    _, column = minimax(board, depth, alpha, beta, True, player, opponent, rows, cols)

    return column


# FUNCTIONS REQUIRED BY THE connect_4_main.py MODULE
def init_agent(player_symbol, board_num_rows, board_num_cols, board):
    """ Inits the agent. Should only need to be called once at the start of a game."""
    global position_cache, ROWS, COLS
    position_cache = {}  # Reset the cache at the start of each game

    # Store the actual board dimensions (even though they're likely fixed)
    ROWS = int(board_num_rows)
    COLS = int(board_num_cols)
    return True


def what_is_your_move(board, game_rows, game_cols, my_game_symbol):
    """ Decide your move, i.e., which column to drop a disk. """
    # Determine opponent's symbol
    opponent_symbol = 'O' if my_game_symbol == 'X' else 'X'

    # Use the global dimensions rather than recalculating
    # Get the best move (0-indexed)
    best_col = get_best_move(board, my_game_symbol, opponent_symbol, ROWS, COLS)

    # Return the move (1-indexed as expected by the main module)
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
    print("MV_Connect_4_Agent.py is intended to be imported and not executed.")
else:
    print("MV_Connect_4_Agent.py has been imported.")