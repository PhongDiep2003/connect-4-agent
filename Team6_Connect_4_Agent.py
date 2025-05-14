# IMPORTS
import random
import math


# DEFINITIONS / REPRESENTATION LOGIC
# Board is a 2D list of characters. ' ' = empty, 'X' and 'O' = player pieces.

# HELPER FUNCTIONS
# Print the Board
def print_board(board):
    """ Prints the connect 4 game board."""
    for row in board:
        print('|' + '|'.join(row) + '|')
    print("-" * (len(board[0]) * 2 + 1))
    print(' ' + ' '.join(str(i + 1) for i in range(len(board[0]))))
    return


def drop_piece(board, col, symbol):
    """Contributors:
    - Jaydev Patel (100%)
    Representation Logic: Drops a piece with the given symbol into the specified column.
    The piece will occupy the lowest available row in that column.
    Returns the row index where the piece lands, or -1 if the column is full."""
    rows = len(board)
    for r in range(rows - 1, -1, -1):  # start from bottom row
        if board[r][col] == ' ':
            board[r][col] = symbol
            return r
    return -1  # column is full


def undo_piece(board, row, col):
    """Contributors:
    - Jaydev Patel (100%)
    Representation Logic: Removes a piece from the board at the given (row, col) position.
    This effectively undoes a move, restoring that cell to empty."""
    board[row][col] = ' '
    return


def is_win_for(board, symbol):
    """Contributors:
    - Jaydev Patel (60%, core algorithm structure)
    - Phong Diep  (40%, optimized check pattern)
    Representation/Reasoning Logic: Checks if the given symbol has four in a row on the board.
    Scans horizontally, vertically, and both diagonal directions for a win."""
    rows = len(board)
    cols = len(board[0])
    # Check horizontal wins
    for r in range(rows):
        for c in range(cols - 3):
            if board[r][c] == symbol and board[r][c + 1] == symbol and board[r][c + 2] == symbol and board[r][
                c + 3] == symbol:
                return True
    # Check vertical wins
    for c in range(cols):
        for r in range(rows - 3):
            if board[r][c] == symbol and board[r + 1][c] == symbol and board[r + 2][c] == symbol and board[r + 3][
                c] == symbol:
                return True
    # Check diagonal (down-right) wins
    for r in range(rows - 3):
        for c in range(cols - 3):
            if board[r][c] == symbol and board[r + 1][c + 1] == symbol and board[r + 2][c + 2] == symbol and \
                    board[r + 3][c + 3] == symbol:
                return True
    # Check diagonal (down-left) wins
    for r in range(rows - 3):
        for c in range(3, cols):
            if board[r][c] == symbol and board[r + 1][c - 1] == symbol and board[r + 2][c - 2] == symbol and \
                    board[r + 3][c - 3] == symbol:
                return True
    return False


# REASONING LOGIC – Heuristic evaluation of board states
def evaluate_window(window, my_symbol, opp_symbol):
    """Contributors:
    - Jaydev Patel (50%, core evaluation logic)
    - Miguel Viray (25%, improved threat detection)
    - Ziming Wang (25%, scoring adjustments)
    Reasoning Logic: Scores a window of four cells for the heuristic evaluation.
    Awards points for windows that are favorable to my_symbol and penalizes ones favorable to opp_symbol."""
    score = 0
    # Favorable patterns for my_symbol
    if window.count(my_symbol) == 4:
        score += 100  # Winning window (4 in a row for me)
    elif window.count(my_symbol) == 3 and window.count(' ') == 1:
        score += 5  # Three of mine and one empty (one move to win)
    elif window.count(my_symbol) == 2 and window.count(' ') == 2:
        score += 2  # Two of mine and two empties
    # Unfavorable patterns (opponent)
    if window.count(opp_symbol) == 3 and window.count(' ') == 1:
        score -= 100  # opponent about to win, play defense
    return score


def evaluate_board(board, my_symbol, opp_symbol):
    """Contributors:
    - Jaydev Patel (40%, board evaluation structure)
    - Miguel Viray (30%, improved center column evaluation)
    - Ziming Wang (30%, diagonal weighting adjustment)
    Reasoning Logic: Heuristic evaluation function for the board state from the perspective of my_symbol.
    Returns a numeric score where higher is better for my_symbol."""
    rows = len(board)
    cols = len(board[0])
    score = 0

    # target center column
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
            window = [board[r][c + i] for i in range(4)]
            score += evaluate_window(window, my_symbol, opp_symbol)
    # Vertical windows
    for c in range(cols):
        for r in range(rows - 3):
            window = [board[r + i][c] for i in range(4)]
            score += evaluate_window(window, my_symbol, opp_symbol)
    # Down-right diagonal windows
    for r in range(rows - 3):
        for c in range(cols - 3):
            window = [board[r + i][c + i] for i in range(4)]
            # Give slightly higher weight to diagonal windows
            score += evaluate_window(window, my_symbol, opp_symbol) * 1.1
            # Down-left diagonal windows
    for r in range(rows - 3):
        for c in range(3, cols):
            window = [board[r + i][c - i] for i in range(4)]
            # Give slightly higher weight to diagonal windows
            score += evaluate_window(window, my_symbol, opp_symbol) * 1.1

    return score


# SEARCH LOGIC – Minimax with Alpha-Beta Pruning
def alpha_beta_search(board, depth, alpha, beta, maximizing_player, my_symbol, opp_symbol):
    """Contributors:
    - Jaydev Patel (50%, core minimax structure)
    - Phong Diep  (30%, alpha-beta pruning optimizations)
    - Ziming Wang (20%, improved terminal condition handling)
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
                return math.inf  # i have won
            elif is_win_for(board, opp_symbol):
                return -math.inf  # opponent has won
            else:
                return 0  # no moves left (draw)
        else:
            # Depth limit reached, return heuristic evaluation
            return evaluate_board(board, my_symbol, opp_symbol)

    # Recursive search with alpha-beta pruning
    if maximizing_player:
        max_eval = -math.inf
        for col in valid_moves:
            # simulate dropping my piece
            row = drop_piece(board, col, my_symbol)
            if row == -1:
                continue  # Skip invalid moves
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
            if row == -1:
                continue  # Skip invalid moves
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


# Order moves to improve alpha-beta pruning efficiency
def order_moves(board, moves, my_symbol):
    """Contributors:
    - Jaydev Patel (60%, core approach)
    - Ziming Wang (30%, center proximity and height-based ordering)
    - Miguel Viray (10%, scoring function)
    Orders moves to improve alpha-beta pruning efficiency.
    Prioritizes center columns and columns where placing a piece results in a higher position."""
    # Start with center columns
    cols = len(board[0])
    center_col = cols // 2

    # Calculate center proximity for each move
    move_scores = []
    for col in moves:
        # Score based on proximity to center and height
        center_distance = abs(col - center_col)
        row = -1
        for r in range(len(board) - 1, -1, -1):
            if board[r][col] == ' ':
                row = r
                break

        # Columns closer to center and pieces higher on the board are preferred
        score = -center_distance - 0.1 * row
        move_scores.append((col, score))

    # Sort by score (descending)
    move_scores.sort(key=lambda x: x[1], reverse=True)
    return [move[0] for move in move_scores]


# FUNCTIONS REQUIRED BY THE connect_4_main.py MODULE
def init_agent(player_symbol, board_num_rows, board_num_cols, board):
    """ Initializes the agent at the start of a game. This function could set up any necessary state."""
    # Set up global variables
    global MY_SYMBOL, OPPONENT_SYMBOL, ROWS, COLS
    MY_SYMBOL = player_symbol
    OPPONENT_SYMBOL = 'O' if player_symbol == 'X' else 'X'
    ROWS = int(board_num_rows)
    COLS = int(board_num_cols)
    return True


def what_is_your_move(board, game_rows, game_cols, my_game_symbol):
    """Contributors:
    - Jaydev Patel (40%, core decision logic and rule-based checks)
    - Phong Diep  (20%, win/block detection)
    - Ziming Wang (15%, move ordering enhancements)
    - Miguel Viray (25%, variable search depth)
    Decide and return the next move (column number) for the agent.
    Applies rule-based reasoning for immediate wins/blocks, then uses Alpha-Beta search for the best move.
    Returns a column index in 1..game_cols (inclusive) to drop a disk."""
    # Update global variables in case of a new game
    global MY_SYMBOL, OPPONENT_SYMBOL, ROWS, COLS
    MY_SYMBOL = my_game_symbol
    OPPONENT_SYMBOL = 'O' if my_game_symbol == 'X' else 'X'
    ROWS = int(game_rows)
    COLS = int(game_cols)

    # REASONING: Rule-based immediate win check
    # If we can win in this move, do it immediately
    for col in range(COLS):
        if board[0][col] != ' ':
            continue  # skip if column is full
        row = drop_piece(board, col, MY_SYMBOL)
        if row != -1 and is_win_for(board, MY_SYMBOL):
            # Undo the simulation and return this winning move immediately
            undo_piece(board, row, col)
            return col + 1  # return 1-indexed column
        # Undo the move if it didn't result in an immediate win
        if row != -1:
            undo_piece(board, row, col)

    # REASONING: Rule-based block opponent's win
    # If the opponent can win next turn, block them by playing that column
    for col in range(COLS):
        if board[0][col] != ' ':
            continue  # skip if column is full
        row = drop_piece(board, col, OPPONENT_SYMBOL)
        if row != -1 and is_win_for(board, OPPONENT_SYMBOL):
            # This column is a winning move for the opponent, so we must block it
            undo_piece(board, row, col)
            return col + 1  # return 1-indexed column
        # Undo the move if it didn't block an immediate win
        if row != -1:
            undo_piece(board, row, col)

    # SEARCH: Use Minimax (Alpha-Beta) to choose the best move if no immediate win/block is found
    best_score = -math.inf
    best_col = None

    # Get all valid columns and order them for better pruning
    valid_columns = [c for c in range(COLS) if board[0][c] == ' ']
    ordered_columns = order_moves(board, valid_columns, MY_SYMBOL)

    # Try each valid move, pick the one with highest score
    for col in ordered_columns:
        # Simulate dropping our piece
        row = drop_piece(board, col, MY_SYMBOL)
        if row == -1:
            continue  # Skip invalid moves (shouldn't happen here)

        # Search with depth 5, starting with opponent's turn (minimizing player)
        # Use variable depth: deeper near the center, shallower on edges
        center_col = COLS // 2
        distance_from_center = abs(col - center_col)
        depth_adjustment = max(0, 2 - distance_from_center)  # Up to 2 extra levels for center columns
        search_depth = 4 + depth_adjustment

        score = alpha_beta_search(board, search_depth, -math.inf, math.inf, False, MY_SYMBOL, OPPONENT_SYMBOL)

        # Undo the move
        undo_piece(board, row, col)

        # Update best move
        if score > best_score:
            best_score = score
            best_col = col
        # If multiple moves have same score, prefer central columns
        elif score == best_score:
            # Calculate center proximity for both current best and new column
            current_distance = abs(best_col - COLS // 2) if best_col is not None else COLS
            new_distance = abs(col - COLS // 2)
            if new_distance < current_distance:
                best_col = col

    # If for some reason no move was chosen (shouldn't happen with valid columns),
    # pick the center column or a random valid column
    if best_col is None:
        center_col = COLS // 2
        if board[0][center_col] == ' ':
            best_col = center_col
        else:
            valid_moves = [c for c in range(COLS) if board[0][c] == ' ']
            best_col = random.choice(valid_moves) if valid_moves else 0

    return best_col + 1  # return as 1-indexed column number


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

    return True


#####
# MAKE SURE MODULE IS IMPORTED
if __name__ == "__main__":
    print("Team6_Connect_4_Agent.py is intended to be imported and not executed.")
else:
    print("Team6_Connect_4_Agent.py has been imported.")
