"""
Tic Tac Toe Player
"""

import math
import copy
X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    stepX = 0
    stepO = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                stepX += 1
            elif board[i][j] == O:
                stepO += 1

    return X if stepX == stepO else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    availableActions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                availableActions.add((i, j))
    return availableActions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Invalid Action")
    if terminal(board):
        raise Exception("Game end")

    newBoard = copy.deepcopy(board)
    newBoard[action[0]][action[1]] = player(board)

    return newBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check row, col
    for i in range(3):
        # row horizontally
        if board[i][0] == board[i][1] == board[i][2] != EMPTY:
            return board[i][0]
        # vertically
        if board[0][i] == board[1][i] == board[2][i] != EMPTY:
            return board[0][i]
    # diagonally.
    if (board[0][0] == board[1][1] == board[2][2] != EMPTY) or (
        board[2][0] == board[1][1] == board[0][2] != EMPTY
    ):
        return board[1][1]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    #  has winner or board filled
    if winner(board) != None:
        return True
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winnerPlayer = winner(board)

    if winnerPlayer == X:
        return 1
    elif winnerPlayer == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    movePlayer = player(board)
    move = None
    if movePlayer == X:
        value = float('-inf')
        for action in actions(board):
            minValue = min_value(result(board, action))
            if minValue > value:
                value = minValue
                move = action
    else:
        value = float('inf')
        for action in actions(board):
            maxValue = max_value(result(board, action))
            if maxValue < value:
                value = maxValue
                move = action
    return move


def max_value(board):
    if terminal(board):
        return utility(board)

    value = float('-inf')
    for action in actions(board):
        value = max(value, min_value(result(board, action)))
    return value


def min_value(board):
    if terminal(board):
        return utility(board)

    value = float('inf')
    for action in actions(board):
        value = min(value, max_value(result(board, action)))
    return value
