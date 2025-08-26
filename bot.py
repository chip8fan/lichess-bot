import berserk
import os
from dotenv import load_dotenv
import secrets
import time
import chess
import chess.polyglot
import sys
import multiprocessing
class Engine():
    def __init__(self):
        load_dotenv()
        self.key = os.environ.get("BOT_KEY")
        self.session = berserk.TokenSession(self.key)
        self.client = berserk.Client(session=self.session)
    def reverse_result(self, result):
        if result == "win":
            return "loss"
        elif result == "loss":
            return "win"
        elif result == "draw":
            return "draw"
    def read_opening_book(self, board):
        with chess.polyglot.open_reader("3000book.bin") as reader:
            try:
                return reader.find(board).move.uci()
            except IndexError:
                return None
    def get_material(self, board=chess.Board):
        pawns = len(board.pieces(chess.PAWN, chess.WHITE)) - len(board.pieces(chess.PAWN, chess.BLACK))
        knights = (len(board.pieces(chess.KNIGHT, chess.WHITE)) - len(board.pieces(chess.KNIGHT, chess.BLACK)))*3
        bishops = (len(board.pieces(chess.BISHOP, chess.WHITE)) - len(board.pieces(chess.BISHOP, chess.BLACK)))*3
        rooks = (len(board.pieces(chess.ROOK, chess.WHITE)) - len(board.pieces(chess.ROOK, chess.BLACK)))*5
        queens = (len(board.pieces(chess.QUEEN, chess.WHITE)) - len(board.pieces(chess.QUEEN, chess.BLACK)))*9
        material = pawns+knights+bishops+rooks+queens
        if board.is_game_over():
            if board.is_checkmate():
                if board.outcome().winner == chess.WHITE:
                    return 1000
                elif board.outcome().winner == chess.BLACK:
                    return -1000
            else:
                return 0
        elif board.can_claim_draw():
            return 0
        return material
    def evaluate(self, all_moves=str, fen=str, depth=int):
        if fen == 'startpos':
            self.board = chess.Board()
        else:
            self.board = chess.Board(fen=fen)
        move_list = str(all_moves).split(" ")
        for move in move_list:
            if move != '':
                self.board.push_uci(move)
        if self.board.turn == chess.WHITE:
            color = 1
        elif self.board.turn == chess.BLACK:
            color = -1
        if len(move_list) <= 20:
            book_move = self.read_opening_book(self.board)
        else:
            book_move = None
        if book_move != None:
            return [self.get_material(self.board), [book_move], True, 1]
        elif len(self.board.piece_map()) <= 7:
            tablebase_data = self.client.tablebase.standard(self.board.fen())
            tablebase_data = [move['uci'] for move in tablebase_data['moves'] if self.reverse_result(move['category']) == tablebase_data['category']]
            return [self.get_material(self.board), tablebase_data, True, 1]
        else:
            nodes = [move.uci() for move in self.board.legal_moves]
            new_list = []
            for node in nodes:
                move = chess.Move.from_uci(node)
                if self.board.gives_check(move):
                    new_list.append([750, node])
                elif self.board.is_capture(move):
                    new_list.append([500+self.mvv_lva(self.board.piece_at(move.from_square), self.board.piece_at(move.to_square)), node])
                else:
                    new_list.append([0, node])
            new_list = sorted(new_list, reverse=True)
            nodes = [node[1] for node in new_list]
            queue = multiprocessing.Queue()
            scores = []
            threads = []
            best_moves = []
            for node in nodes:
                temp_board = self.board.copy()
                temp_board.push_uci(node)
                threads.append(multiprocessing.Process(target=self.negamax_wrapper, args=(temp_board, depth, color, queue, node)))
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            while not queue.empty():
                scores.append(queue.get())
            max_score = max([move[0] for move in scores])
            max_moves = max([move[2] for move in scores])
            for move in scores:
                if move[0] == max_score:
                    best_moves.append(move[1])
            return [max_score, best_moves, False, max_moves]
    def negamax_wrapper(self, board=chess.Board, depth=int, color=int, queue=multiprocessing.Queue, most_recent_move=str):
        score = self.negamax(board, depth-1, -sys.maxsize, sys.maxsize, -color)
        queue.put([-score[0], most_recent_move, score[1]])
    def negamax(self, board=chess.Board, depth=int, alpha=int, beta=int, color=int): # implementation in python of wikipedia's pseudocode of the base negamax algorithm with alpha-beta pruning
        if board.is_game_over() or board.can_claim_draw() or depth == 0:
            return [color*self.get_material(board), len(list(board.legal_moves))]
        value = -sys.maxsize
        nodes = [move.uci() for move in board.legal_moves]
        new_list = []
        for node in nodes:
            move = chess.Move.from_uci(node)
            if board.gives_check(move):
                new_list.append([750, node])
            elif board.is_capture(move):
                new_list.append([500+self.mvv_lva(board.piece_at(move.from_square), board.piece_at(move.to_square)), node])
            else:
                new_list.append([0, node])
        new_list = sorted(new_list, reverse=True)
        nodes = [node[1] for node in new_list]
        for node in nodes:
            board.push_uci(node)
            value = max(-self.negamax(board, depth-1, -beta, -alpha, -color)[0], value)
            board.pop()
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return [value, len(list(board.legal_moves))]
    def mvv_lva(self, aggressor, victim):
        difference = 0
        if aggressor == chess.PAWN:
            difference -= 1
        elif aggressor == chess.KNIGHT:
            difference -= 2
        elif aggressor == chess.BISHOP:
            difference -= 3
        elif aggressor == chess.ROOK:
            difference -= 4
        elif aggressor == chess.QUEEN:
            difference -= 5
        elif aggressor == chess.KING:
            difference -= 6
        if victim == chess.PAWN:
            difference += 10
        elif victim == chess.KNIGHT or victim == chess.BISHOP:
            difference += 30
        elif victim == chess.ROOK:
            difference += 50
        elif victim == chess.QUEEN:
            difference += 90
        return difference
num = 1
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
chess_engine = Engine()
count = 0
def make_move(move_list, time_limit):
    depth = 1
    start = time.perf_counter()
    while time.perf_counter()-start < time_limit and depth <= 10:
        print(f"depth={depth}")
        if __name__ == "__main__":
            moves = chess_engine.evaluate(move_list, fen, depth)
        move = moves[1][secrets.randbelow(len(moves[1]))]
        depth += 1
        if abs(moves[0]) == 1000 or moves[2] == True:
            break
        if time.perf_counter()-start > time_limit/moves[3]:
            break
    client.bots.make_move(game_id, move)
if isMyTurn:
    if time_remaining != 'unlimited':
        make_move("", time_remaining/num)
    else:
        make_move("", 60*60*24)
    isMyTurn = False
elif color == "white" and fen == "startpos":
    if time_remaining != 'unlimited':
        make_move("", time_remaining/num)
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
                make_move(response['moves'], time_remaining/num)
            else:
                make_move(response['moves'], 60*60*24)
    else:
        if response.get("initialFen") != None:
            fen = response['initialFen']