import tkinter as tk
from tkinter import messagebox
from itertools import product
import time

# Board size
SIZE = 3

# Define the 3D board
board = [[[0 for _ in range(SIZE)] for _ in range(SIZE)] for _ in range(SIZE)]

# Create the root window
root = tk.Tk()
root.title("3D Tic Tac Toe")

def check_winner(board):
    directions = list(product([-1, 0, 1], repeat=3))
    directions.remove((0, 0, 0))

    for x, y, z in product(range(SIZE), repeat=3):
        if board[x][y][z] == 0:
            continue

        for dx, dy, dz in directions:
            nx, ny, nz = x + 2 * dx, y + 2 * dy, z + 2 * dz
            if 0 <= nx < SIZE and 0 <= ny < SIZE and 0 <= nz < SIZE:
                if all(board[x + i * dx][y + i * dy][z + i * dz] == board[x][y][z] for i in range(3)):
                    return board[x][y][z]

    if all(board[x][y][z] != 0 for x, y, z in product(range(SIZE), repeat=3)):
        return -2

    return 0

def evaluate(board):
    score = 0

    # Check rows, columns, and layers
    for i in range(SIZE):
        for j in range(SIZE):
            score += evaluate_line(board, [(i, j, k) for k in range(SIZE)])  # row
            score += evaluate_line(board, [(i, k, j) for k in range(SIZE)])  # column
            score += evaluate_line(board, [(k, i, j) for k in range(SIZE)])  # layer

    # Check diagonals
    for i in range(SIZE):
        score += evaluate_line(board, [(i, j, j) for j in range(SIZE)])  # diagonal 1
        score += evaluate_line(board, [(i, j, SIZE - 1 - j) for j in range(SIZE)])  # diagonal 2
        score += evaluate_line(board, [(j, i, j) for j in range(SIZE)])  # diagonal 3
        score += evaluate_line(board, [(j, i, SIZE - 1 - j) for j in range(SIZE)])  # diagonal 4
        score += evaluate_line(board, [(j, j, i) for j in range(SIZE)])  # diagonal 5
        score += evaluate_line(board, [(j, SIZE - 1 - j, i) for j in range(SIZE)])  # diagonal 6

    # Check cube diagonals
    score += evaluate_line(board, [(i, i, i) for i in range(SIZE)])  # diagonal 1
    score += evaluate_line(board, [(i, i, SIZE - 1 - i) for i in range(SIZE)])  # diagonal 2
    score += evaluate_line(board, [(i, SIZE - 1 - i, i) for i in range(SIZE)])  # diagonal 3
    score += evaluate_line(board, [(i, SIZE - 1 - i, SIZE - 1 - i) for i in range(SIZE)])  # diagonal 4

    return score

def evaluate_line(board, cells):
    line_score = 0
    ai_count, player_count = 0, 0

    for x, y, z in cells:
        if board[x][y][z] == 1:
            ai_count += 1
        elif board[x][y][z] == -1:
            player_count += 1

    if player_count == 0:
        line_score += 10 ** ai_count
    elif ai_count == 0:
        line_score -= (10 ** player_count) * 2  # Increase the weight of blocking opponent's winning lines

    return line_score

# New function to sort possible moves based on their evaluation
def sort_moves(board, maximizing_player):
    moves = [(x, y, z) for x, y, z in product(range(SIZE), repeat=3) if board[x][y][z] == 0]
    move_evals = []

    for x, y, z in moves:
        board[x][y][z] = 1 if maximizing_player else -1
        move_eval = evaluate(board)
        board[x][y][z] = 0
        move_evals.append(move_eval)

    sorted_moves = [move for _, move in sorted(zip(move_evals, moves), key=lambda pair: pair[0], reverse=maximizing_player)]
    return sorted_moves


# Modified Minimax algorithm function
def minimax(board, depth, alpha, beta, maximizing_player):
    winner = check_winner(board)
    if winner != 0 or depth == 0:
        return evaluate(board) if maximizing_player else -evaluate(board)

    if maximizing_player:
        max_eval = float('-inf')
        for x, y, z in sort_moves(board, True):
            board[x][y][z] = 1
            eval = minimax(board, depth - 1, alpha, beta, False)
            board[x][y][z] = 0
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for x, y, z in sort_moves(board, False):
            board[x][y][z] = -1
            eval = minimax(board, depth - 1, alpha, beta, True)
            board[x][y][z] = 0
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def ai_move():
    start_time = time.time()
    max_depth = 1
    best_move = None

    while time.time() - start_time < 5:  # Limit the AI's search time to 5 seconds
        best_value = float('-inf')
        current_best_move = None

        for x, y, z in product(range(SIZE), repeat=3):
            if board[x][y][z] == 0:
                board[x][y][z] = 1
                value = minimax(board, max_depth - 1, float('-inf'), float('inf'), False)
                board[x][y][z] = 0

                if value > best_value:
                    best_value = value
                    current_best_move = (x, y, z)

        max_depth += 1
        best_move = current_best_move

    board[best_move[0]][best_move[1]][best_move[2]] = 1
    update_buttons()

def winning_line(board):
    directions = list(product([-1, 0, 1], repeat=3))
    directions.remove((0, 0, 0))

    for x, y, z in product(range(SIZE), repeat=3):
        if board[x][y][z] == 0:
            continue

        for dx, dy, dz in directions:
            nx, ny, nz = x + 2 * dx, y + 2 * dy, z + 2 * dz
            if 0 <= nx < SIZE and 0 <= ny < SIZE and 0 <= nz < SIZE:
                if all(board[x + i * dx][y + i * dy][z + i * dz] == board[x][y][z] for i in range(3)):
                    return [(x + i * dx, y + i * dy, z + i * dz) for i in range(3)]
    return []

def update_buttons(winning_cells=[]):
    for x, y, z in product(range(SIZE), repeat=3):
        if board[x][y][z] == 1:
            buttons[x][y][z].config(text="X", state=tk.DISABLED)
            if (x, y, z) in winning_cells:
                buttons[x][y][z].config(bg="green")
        elif board[x][y][z] == -1:
            buttons[x][y][z].config(text="O", state=tk.DISABLED)
            if (x, y, z) in winning_cells:
                buttons[x][y][z].config(bg="green")

def button_click(x, y, z):
    if board[x][y][z] == 0:
        board
        board[x][y][z] = -1
        update_buttons()
        winner = check_winner(board)
        if winner == -1:
            tk.messagebox.showinfo("Game Over", "You won!")
            root.quit()
        elif winner == -2:
            tk.messagebox.showinfo("Game Over", "It's a draw!")
            root.quit()
        else:
            ai_move()
            winner = check_winner(board)
            if winner == 1:
                winning_cells = winning_line(board)
                update_buttons(winning_cells)
                tk.messagebox.showinfo("Game Over", "AI won!")
                root.quit()
            elif winner == -2:
                tk.messagebox.showinfo("Game Over", "It's a draw!")
                root.quit()
            

# Create buttons
buttons = [[[tk.Button(root, text="", command=lambda x=x, y=y, z=z: button_click(x, y, z), width=10, height=3)
             for z in range(SIZE)] for y in range(SIZE)] for x in range(SIZE)]

# Create labels for the layers
layer_labels = [tk.Label(root, text=f"Layer {i+1}", font=("Arial", 14)) for i in range(SIZE)]

# Create vertical line separators
def create_separator(column):
    separator_canvas = tk.Canvas(root, width=4, height=120, bg="black")
    separator_canvas.grid(row=0, rowspan=SIZE, column=column, columnspan=1)

# Position the buttons and labels on the grid
for x, y, z in product(range(SIZE), repeat=3):
    buttons[x][y][z].grid(row=y, column=(z + x * (SIZE + 1)))
    layer_labels[x].grid(row=SIZE, column=(x * (SIZE + 1)) + 1)

    if x < SIZE - 1 and z == SIZE - 1:
        create_separator((x + 1) * (SIZE + 1) - 1)

root.mainloop()
