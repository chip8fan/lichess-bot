import chess
import sys
class Engine():
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
        nodes = sorted([str(move).replace("Move.from_uci('", "").replace("')", "") for move in list(board.legal_moves)])
        moves = []
        for node in nodes:
            temp_board = board.copy()
            temp_board.push_uci(node)
            negamax = -self.negamax(temp_board, depth-1, -color)[0]
            if negamax > value:
                moves.clear()
                moves.append(node)
                value = negamax
            elif negamax == value:
                moves.append(node)
        return [value, moves]
