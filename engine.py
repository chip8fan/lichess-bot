import chess
import chess.polyglot
import sys
import time
import os
import berserk
from dotenv import load_dotenv
class Super_Slow_Engine():
    def __init__(self):
        pass
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
        return self.negamax(self.board, depth, color)
    def negamax(self, board=chess.Board, depth=int, color=int): # implementation in python of wikipedia's pseudocode of the base negamax algorithm
        if depth == 0 or board.is_game_over():
            return [color*self.get_material(board)]
        value = -sys.maxsize
        nodes = sorted([move.uci() for move in board.legal_moves])
        moves = []
        for node in nodes:
            board.push_uci(node)
            negamax = -self.negamax(board, depth-1, -color)[0]
            board.pop()
            if negamax > value:
                moves.clear()
                moves.append(node)
                value = negamax
            elif negamax == value:
                moves.append(node)
        return [value, moves]
class Engine():
    def __init__(self):
        load_dotenv()
        self.key = os.environ.get("BOT_KEY")
        self.session = berserk.TokenSession(self.key)
        self.client = berserk.Client(session=self.session)
        self.transposition_table = {

        }
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
            return [self.get_material(self.board), [book_move], True]
        elif len(self.board.piece_map()) <= 7:
            tablebase_data = self.client.tablebase.standard(self.board.fen())
            tablebase_data = [move['uci'] for move in tablebase_data['moves'] if self.reverse_result(move['category']) == tablebase_data['category']]
            return [self.get_material(self.board), tablebase_data, True]
        else:
            high_score = -sys.maxsize
            best_moves = []
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
            for node in nodes:
                self.board.push_uci(node)
                score = -self.negamax(self.board, depth-1, -sys.maxsize, sys.maxsize, -color)
                self.board.pop()
                if score > high_score:
                    best_moves.clear()
                    best_moves.append(node)
                    high_score = score
                elif score == high_score:
                    best_moves.append(node)
            return [high_score, best_moves, False]
    def negamax(self, board=chess.Board, depth=int, alpha=int, beta=int, color=int): # implementation in python of wikipedia's pseudocode of the base negamax algorithm with alpha-beta pruning
        key = board.fen()
        if key in self.transposition_table:
            cached = self.transposition_table[key]
            if cached['depth'] >= depth:
                return cached['score']
        if board.is_game_over() or board.can_claim_draw() or depth == 0:
            score = color*self.get_material(board)
            self.transposition_table[key] = {'score': score, 'depth': depth}
            return score
        value = -sys.maxsize
        nodes = [move.uci() for move in board.legal_moves]
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
        for node in nodes:
            board.push_uci(node)
            value = max(-self.negamax(board, depth-1, -beta, -alpha, -color), value)
            board.pop()
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        self.transposition_table[key] = {'score': value, 'depth': depth}
        return value
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
if __name__ == "__main__":
    engine = Engine()
    start = time.perf_counter()
    evaluation = engine.evaluate("e2e4 e7e5", "startpos", 4)
    print(evaluation)
    end = time.perf_counter()-start
    print(f"evaluation completed in {end} seconds by engine")
