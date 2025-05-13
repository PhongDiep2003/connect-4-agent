# Team1_Connect_4_Agent.py – Connect 4 AI using Minimax + Alpha-Beta Pruning
import random

MAX_DEPTH = 5  # Depth of lookahead for minimax (increase for a stronger AI if performance allows)

# Global variables to store state (set in init_agent)
MY_SYMBOL = None
OPPONENT_SYMBOL = None
ROWS = 0
COLS = 0

# Helper: print the board (for debugging or optional use)
def print_board(board):
    """Prints the Connect 4 board state to the console."""
    for row in board:
        print('|' + '|'.join(row) + '|')
    print('-' * (len(board[0]) * 2 + 1))
    print(' ' + ' '.join(str(i+1) for i in range(len(board[0]))))

# Required Function 1: Initialize the agent
def init_agent(player_symbol, board_num_rows, board_num_cols, board):
    """Called once at the start of a game to initialize the agent's settings."""
    global MY_SYMBOL, OPPONENT_SYMBOL, ROWS, COLS
    MY_SYMBOL = player_symbol                        # e.g. 'X' or 'O' for this agent
    OPPONENT_SYMBOL = 'O' if player_symbol == 'X' else 'X'
    ROWS = int(board_num_rows)
    COLS = int(board_num_cols)
    # (We don't need to retain the board here since we'll use the board passed to what_is_your_move)
    return True

# Helper: check if a given player has a connect-4 win on the board
def is_win(board, piece):
    """Returns True if the given piece ('X' or 'O') has four in a row on the board."""
    # Check horizontal streaks
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Check vertical streaks
    for c in range(COLS):
        for r in range(ROWS - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    # Check positively sloped diagonals (down-right)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    # Check negatively sloped diagonals (down-left)
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if board[r][c] == piece and board[r+1][c-1] == piece and board[r+2][c-2] == piece and board[r+3][c-3] == piece:
                return True
    return False

# Helper: evaluate a 4-cell window for a given perspective piece
def evaluate_window(window, piece):
    """Scores a 4-cell window of the board for the given piece's advantage."""
    score = 0
    empty = ' '
    opp_piece = OPPONENT_SYMBOL if piece == MY_SYMBOL else MY_SYMBOL  # opponent of the piece we are evaluating for
    # Scoring rules as per our heuristic:
    if window.count(piece) == 4:
        score += 100  # Winning window (4 of my pieces)
    elif window.count(piece) == 3 and window.count(empty) == 1:
        score += 5    # 3 of my pieces and 1 empty space (good chance to win)
    elif window.count(piece) == 2 and window.count(empty) == 2:
        score += 2    # 2 of my pieces and 2 empties (potential alignment)
    # If the opponent is about to win, add a penalty to encourage blocking:
    if window.count(opp_piece) == 3 and window.count(empty) == 1:
        score -= 4    # 3 opponent pieces and 1 empty (opponent could win next move)
    return score

# Helper: heuristic score of the entire board for the agent (MY_SYMBOL)
def score_position(board, piece):
    """Computes a heuristic score for the board from the perspective of the given piece."""
    # Higher score means the board is better for 'piece'. We will call this for MY_SYMBOL.
    score = 0
    # Center column preference: count my pieces in the center column and weight them
    center_col = COLS // 2
    center_count = sum(1 for r in range(ROWS) if board[r][center_col] == piece)
    score += center_count * 3  # add 3 points for each piece in the center column

    # Evaluate all possible windows of 4 cells in the board
    for r in range(ROWS):
        for c in range(COLS - 3):  # horizontal window
            window = [board[r][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
    for c in range(COLS):
        for r in range(ROWS - 3):  # vertical window
            window = [board[r+i][c] for i in range(4)]
            score += evaluate_window(window, piece)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):  # positive diagonal window (down-right)
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
    for r in range(ROWS - 3):
        for c in range(3, COLS):   # negative diagonal window (down-left)
            window = [board[r+i][c-i] for i in range(4)]
            score += evaluate_window(window, piece)
    return score

# Helper: get list of columns that are valid for a move (not already full)
def get_valid_moves(board):
    """Returns a list of column indices (0-based) that are not full and can accept a new piece."""
    valid_columns = []
    for c in range(COLS):
        if board[0][c] == ' ':  # if top cell is empty, the column c can be played
            valid_columns.append(c)
    return valid_columns

# Helper: get the next open row in a given column
def get_next_open_row(board, col):
    """Finds the lowest empty row index in the given column (for dropping a piece)."""
    for r in range(ROWS-1, -1, -1):  # start from bottom row and go upward
        if board[r][col] == ' ':
            return r
    return None  # column is full

# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Minimax search: returns (best_col, best_score) for the current board.
    - depth: remaining depth to search
    - alpha, beta: alpha-beta pruning bounds
    - maximizing_player: True if it's the agent's turn, False if it's the opponent's turn
    """
    valid_cols = get_valid_moves(board)
    # Check terminal conditions (win or draw) to end recursion
    if is_win(board, MY_SYMBOL):
        return (None, 1000000)   # Large positive score for win
    if is_win(board, OPPONENT_SYMBOL):
        return (None, -1000000)  # Large negative score for loss
    if not valid_cols:  # No moves left (board is full) -> draw
        return (None, 0)
    if depth == 0:
        # Depth limit reached; evaluate board heuristically
        return (None, score_position(board, MY_SYMBOL))
    
    if maximizing_player:
        # Agent's turn (maximize score)
        best_score = -float('inf')
        best_col = random.choice(valid_cols)  # default to a random valid move (will be replaced by a better move if found)
        for col in valid_cols:
            row = get_next_open_row(board, col)
            if row is not None:
                # Simulate the move
                temp_board = [board[r][:] for r in range(ROWS)]  # make a copy of the board
                temp_board[row][col] = MY_SYMBOL
                # Recurse for opponent's turn
                _, score = minimax(temp_board, depth-1, alpha, beta, False)
                if score > best_score:
                    best_score = score
                    best_col = col
                # Update alpha and prune if possible
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break  # alpha-beta cutoff
        return (best_col, best_score)
    else:
        # Opponent's turn (minimize score for the agent)
        worst_score = float('inf')
        best_col = random.choice(valid_cols)
        for col in valid_cols:
            row = get_next_open_row(board, col)
            if row is not None:
                # Simulate opponent's move
                temp_board = [board[r][:] for r in range(ROWS)]
                temp_board[row][col] = OPPONENT_SYMBOL
                # Recurse for agent's turn
                _, score = minimax(temp_board, depth-1, alpha, beta, True)
                if score < worst_score:
                    worst_score = score
                    best_col = col
                # Update beta and prune if possible
                beta = min(beta, worst_score)
                if alpha >= beta:
                    break
        return (best_col, worst_score)

# Required Function 2: Decide the next move
def what_is_your_move(board, game_rows, game_cols, my_game_symbol):
    """Determines the column number (1-indexed) for the agent's next move."""
    # Update global variables with current game state (in case not retained between calls)
    global MY_SYMBOL, OPPONENT_SYMBOL, ROWS, COLS
    MY_SYMBOL = my_game_symbol
    OPPONENT_SYMBOL = 'O' if my_game_symbol == 'X' else 'X'
    ROWS = int(game_rows)
    COLS = int(game_cols)
    # Use minimax search to choose the best move
    best_col, _ = minimax(board, MAX_DEPTH, -float('inf'), float('inf'), True)
    if best_col is None:
        best_col = 0  # if no moves (should only happen on a full board), choose 0 as a fallback
    return best_col  
# Optional: function called at game end (not critical for decision-making)
def connect_4_result(board, winner, looser):
    """
    Called when the game is over. 
    Prints out the result from this agent's perspective (Team1 in this example).
    """
    if winner == "Draw":
        print(">>> I am player TEAM1 <<<")
        print(">>> The game resulted in a draw. <<<\n")
    else:
        print(">>> I am player TEAM1 <<<")
        print("The winner is " + winner)
        if winner == "Team1":
            print("YEAH!!  :-)")    # cheer if this agent (Team1) won
        else:
            print("BOO HOO HOO  :~(")  # otherwise, lament the loss
        print("The looser is " + looser)
        print()
    return True

# Ensure the module is used as an import, not executed directly
if __name__ == "__main__":
    print("Team1_Connect_4_Agent.py is intended to be imported and not executed.")
else:
    print("Team1_Connect_4_Agent.py has been imported.")