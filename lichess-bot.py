import berserk
from dotenv import load_dotenv
import os
import time
import chess
import random
import sys
def get_legal_moves(moves_list, position=""):
    moves_list = moves_list.split(" ")
    if position == 'startpos':
        board = chess.Board()
    else:
        board = chess.Board(fen=position)
    for move in moves_list:
        try:
            board.push_uci(move)
        except chess.InvalidMoveError:
            pass
    return [str(move).replace("Move.from_uci('", "").replace("')", "") for move in list(board.legal_moves)]
load_dotenv()
key = os.environ.get("BOT_KEY")
session = berserk.TokenSession(key)
client = berserk.Client(session=session)
for response in client.bots.stream_incoming_events():
    if response['type'] == "gameStart":
        game_id = response['game']['gameId']
        break
    elif response['type'] == "challenge":
        print(response)
        game_id = response['challenge']['id']
        if response['challenge']['finalColor'] == "white":
            client.bots.decline_challenge(game_id, "This bot can only play as white.")
            sys.exit()
        if response['challenge']['rated'] == True:
            client.bots.decline_challenge(game_id, "This bot can only play casual games.")
            sys.exit()
        else:
            client.bots.accept_challenge(game_id)
        break
for response in client.bots.stream_game_state(game_id):
    try:
        moves = response['moves']
    except KeyError:
        moves = response['state']['moves']
    try:
        start_pos = response['initialFen']
    except KeyError:
        pass
    break
while True:
    move = random.choice(get_legal_moves(moves, start_pos))
    client.bots.make_move(game_id, move)
    for response in client.bots.stream_game_state(game_id):
        try:
            moves = response['moves']
        except KeyError:
            moves = response['state']['moves']
        try:
            start_pos = response['initialFen']
        except KeyError:
            pass
        if str(moves).endswith(move) == False:
            break
    time.sleep(1)