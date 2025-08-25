import berserk
import os
from dotenv import load_dotenv
import engine
import secrets
import time
def not_empty(moves):
    if moves == ['']:
        return 0
    else:
        return len(moves)
def invert_color(color):
    if color == "white":
        return "black"
    elif color == "black":
        return "white"
load_dotenv()
key = os.environ.get("BOT_KEY")
session = berserk.TokenSession(key)
client = berserk.Client(session=session)
isMyTurn = False
fen = 'startpos'
for response in client.bots.stream_incoming_events():
    if response.get("type") == "challenge":
        game_id = response['challenge']['id']
        color = invert_color(response['challenge']['finalColor'])
        client.bots.accept_challenge(game_id)
        speed = response['challenge']['speed']
        try:
            time_remaining = response['challenge']['timeControl']['limit']
        except KeyError:
            time_remaining = 'unlimited'
        break
    elif response.get("type") == "gameStart":
        fen = response['game']['fen']
        game_id = response['game']['gameId']
        isMyTurn = response['game']['isMyTurn']
        color = response['game']['color']
        speed = response['game']['speed']
        try:
            time_remaining = response['game']['secondsLeft']
        except KeyError:
            time_remaining = 'unlimited'
        break
chess_engine = engine.Engine()
count = 0
def make_move(move_list, time_limit):
    depth = 1
    start = time.perf_counter()
    while time.perf_counter()-start < time_limit and depth <= 100:
        moves = chess_engine.evaluate(move_list, fen, depth)
        move = moves[1][secrets.randbelow(len(moves[1]))]
        depth += 1
        if abs(moves[0]) == 1000 or moves[2] == True:
            break
    client.bots.make_move(game_id, move)
if isMyTurn:
    if time_remaining != 'unlimited':
        make_move("", time_remaining/200)
    else:
        make_move("", 60*60*24)
    isMyTurn = False
elif color == "white" and fen == "startpos":
    if time_remaining != 'unlimited':
        make_move("", time_remaining/200)
    else:
        make_move("", 60*60*24)
for response in client.bots.stream_game_state(game_id):
    if response.get("type") == "gameState":
        if color == "black":
            if time_remaining != 'unlimited':
                time_remaining = (response['btime'].hour*3600)+(response['btime'].minute*60)+(response['btime'].second)
                if speed == 'correspondence':
                    time_remaining += response['btime'].day*86400
        elif color == "white":
            if time_remaining != 'unlimited':
                time_remaining = (response['wtime'].hour*3600)+(response['wtime'].minute*60)+(response['wtime'].second)
                if speed == 'correspondence':
                    time_remaining += response['wtime'].day*86400
        count = not_empty(str(response['moves']).split(' '))
        bot_turn = (count%2==1 and color=="black") or (count%2==0 and color=="white")
        if bot_turn:
            if time_remaining != 'unlimited':
                make_move(response['moves'], time_remaining/200)
            else:
                make_move(response['moves'], 60*60*24)
    else:
        if response.get("initialFen") != None:
            fen = response['initialFen']
