import berserk # python wrapper for lichess API
from dotenv import load_dotenv # load dotenv
import os # get the environment variable using the os library
import chess # core chess logic that makes valid random moves possible
import random # random library (might replace with secrets)
import sys # to exit the program if it is needed
import time # to rate-limit requests to the lichess API
def get_legal_moves(moves_list, position=""): # get_legal_moves is almost identical to is_game_over
    moves_list = moves_list.split(" ") # get the individual moves
    if position == 'startpos': # if the initial FEN is startpos
        board = chess.Board() # initialize a chess.Board()
    else: # if the initial FEN is NOT startpos
        board = chess.Board(fen=position) # load a chess.Board() with the fen
    for move in moves_list: # get each move in the move list
        if move != '': # if move is not empty
            board.push_uci(move) # make the move
    return [str(move).replace("Move.from_uci('", "").replace("')", "") for move in list(board.legal_moves)] # return a list of legal moves
def is_game_over(moves_list, position=""): # is_game_over is nearly an identical function to get_legal_moves
    moves_list = moves_list.split(" ") # get the individual moves
    if position == 'startpos': # if the initial FEN is startpos
        board = chess.Board() # initialize a chess.Board()
    else: # if the initial FEN is NOT startpos
        board = chess.Board(fen=position) # load a chess.Board() with the fen
    for move in moves_list: # get each move in the move list
        try: # try to make a move
            board.push_uci(move) # make the move
        except chess.InvalidMoveError: # EXCEPT if the move is invalid
            pass # then ignore the move
    return board.is_game_over() # return if the game is over or not
load_dotenv() # load the .env file
key = os.environ.get("BOT_KEY") # get the BOT_KEY from the .env file (the secure way to store environment variables, NEVER hardcode a key into an app)
session = berserk.TokenSession(key) # initialize a session
client = berserk.Client(session=session) # and a client
for response in client.bots.stream_incoming_events(): # check for challenges and gameStart events
    if response['type'] == "gameStart": # if a gameStart event happens
        game_id = response['game']['gameId'] # set the game_id
        break # and exit the loop
    elif response['type'] == "challenge": # if a challenge event happens
        print(response) # log the response
        game_id = response['challenge']['id'] # and get the game id
        if response['challenge']['rated'] == True: # check if the challenge is rated
            client.bots.decline_challenge(game_id, "This bot can only play casual games.") # if it is, decline the challenge
            sys.exit() # and exit
        else: # otherwise
            client.bots.accept_challenge(game_id) # accept the challenge
        break # and exit the loop
for response in client.bots.stream_game_state(game_id): # check for moves
    try: # try to get the moves
        moves = response['moves'] # get the moves
    except KeyError: # but if this doesn't work
        moves = response['state']['moves'] # then this should work
    start_pos = response['initialFen'] # set the start position to the initial FEN
    break # and exit the loop
while True: # while bot is running
    try: # try to make a move
        move = random.choice(get_legal_moves(moves, start_pos)) # get a random move
        client.bots.make_move(game_id, move) # and make the move
    except berserk.exceptions.ResponseError: # but if the bot does NOT get the first move
        pass # then it will throw an error, which will be ignored
    for response in client.bots.stream_game_state(game_id): # get the events in the game
        try: # try to get the moves
            moves = response['moves'] # get the moves
        except KeyError: # but if this doesn't work
            moves = response['state']['moves'] # then this should work
        if str(moves).endswith(move) == False: # check if the other side has made a move
            break # if they have, break
    time.sleep(1) # sleep to prevent 429
# problem: if a challenge is accepted but then an abort happens, the bot is simply in a blocking mode until it makes too many requests (which throws a 429 Client Error)