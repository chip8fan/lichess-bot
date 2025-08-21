import berserk # python wrapper for lichess API
from dotenv import load_dotenv # load dotenv
import os # get the environment variable using the os library
import secrets # random library but more secure
import sys # to exit the program if it is needed
import engine
import time
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
        if response['challenge']['speed'] == 'ultraBullet': # check if challenge is ultrabullet
            client.bots.decline_challenge(game_id, "This bot cannot play ultrabullet.") # if it is an ultrabullet challenge reject it
            sys.exit() # and exit
        else:
            client.bots.accept_challenge(game_id)
        break # and exit the loop
for response in client.bots.stream_game_state(game_id): # check for moves
    try: # try to get the moves
        moves = response['moves'] # get the moves
    except KeyError: # but if this doesn't work
        moves = response['state']['moves'] # then this should work
    start_pos = response['initialFen'] # set the start position to the initial FEN
    break # and exit the loop
error_count = 0 # count the amount of errors
chess_engine = engine.Engine()
while True: # while bot is running
    c = 0 # counter for artificial timeout
    try: # try to make a move
        start = time.perf_counter()
        legal_moves = chess_engine.evaluate(all_moves=moves, fen=start_pos, depth=4)
        move = legal_moves[1][secrets.randbelow(len(legal_moves))] # get a random move
        end = time.perf_counter()-start
        print(legal_moves)
        print(f"{move} made in {end} seconds, eval {legal_moves[0]}")
        client.bots.make_move(game_id, move) # and make the move
    except berserk.exceptions.ResponseError: # but if the bot does NOT get the first move
        error_count += 1 # add an error
    if error_count >= 10: # if too many errors
        sys.exit() # exit
    for response in client.bots.stream_game_state(game_id): # get the events in the game
        try: # try to get the moves
            moves = response['moves'] # get the moves
        except KeyError: # but if this doesn't work
            moves = response['state']['moves'] # then this should work
        if str(moves).endswith(move) == False or c >= 10: # check if the other side has made a move or the counter is 10 (an artificial timeout)
            break # if they have, break
        c += 1 # increment the counter by 1
