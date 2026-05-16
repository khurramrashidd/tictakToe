from flask import Flask, render_template, jsonify, request, session
import json

app = Flask(__name__)
app.secret_key = 'tictactoe_secret_key_2024'

def check_winner(board):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],  # rows
        [0,3,6],[1,4,7],[2,5,8],  # cols
        [0,4,8],[2,4,6]            # diags
    ]
    for combo in wins:
        if board[combo[0]] and board[combo[0]] == board[combo[1]] == board[combo[2]]:
            return board[combo[0]], combo
    if all(board):
        return 'draw', []
    return None, []

def minimax(board, is_maximizing):
    winner, _ = check_winner(board)
    if winner == 'O': return 10
    if winner == 'X': return -10
    if winner == 'draw': return 0

    if is_maximizing:
        best = -1000
        for i in range(9):
            if not board[i]:
                board[i] = 'O'
                best = max(best, minimax(board, False))
                board[i] = ''
        return best
    else:
        best = 1000
        for i in range(9):
            if not board[i]:
                board[i] = 'X'
                best = min(best, minimax(board, True))
                board[i] = ''
        return best

def best_move(board):
    best_val = -1000
    move = -1
    for i in range(9):
        if not board[i]:
            board[i] = 'O'
            val = minimax(board, False)
            board[i] = ''
            if val > best_val:
                best_val = val
                move = i
    return move

@app.route('/')
def index():
    session['board'] = [''] * 9
    session['current'] = 'X'
    session['scores'] = session.get('scores', {'X': 0, 'O': 0, 'draw': 0})
    return render_template('index.html', scores=session['scores'])

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    board = session.get('board', [''] * 9)
    idx = data.get('index')
    mode = data.get('mode', 'pvp')

    if board[idx] or check_winner(board)[0]:
        return jsonify({'error': 'Invalid move'})

    board[idx] = 'X'
    winner, combo = check_winner(board)

    if not winner and mode == 'ai':
        ai_idx = best_move(board)
        if ai_idx != -1:
            board[ai_idx] = 'O'
            winner, combo = check_winner(board)

    session['board'] = board

    scores = session.get('scores', {'X': 0, 'O': 0, 'draw': 0})
    if winner and winner != 'draw':
        scores[winner] = scores.get(winner, 0) + 1
    elif winner == 'draw':
        scores['draw'] = scores.get('draw', 0) + 1
    session['scores'] = scores

    return jsonify({
        'board': board,
        'winner': winner,
        'combo': combo,
        'scores': scores
    })

@app.route('/reset', methods=['POST'])
def reset():
    session['board'] = [''] * 9
    session['current'] = 'X'
    return jsonify({'board': [''] * 9, 'scores': session.get('scores', {'X': 0, 'O': 0, 'draw': 0})})

@app.route('/reset_scores', methods=['POST'])
def reset_scores():
    session['scores'] = {'X': 0, 'O': 0, 'draw': 0}
    session['board'] = [''] * 9
    return jsonify({'scores': session['scores']})

if __name__ == '__main__':
    app.run(debug=True)