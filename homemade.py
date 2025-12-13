import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.lichess_types import MOVE, HOMEMADE_ARGS_TYPE
import logging
import engine
logger = logging.getLogger(__name__)
class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""
class Engine(ExampleEngine):
    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:
        if isinstance(time_limit.time, float):
            my_time = time_limit.time
            my_inc = 0
        elif board.turn == chess.WHITE:
            my_time = time_limit.white_clock if isinstance(time_limit.white_clock, float) else 0
            my_inc = time_limit.white_inc if isinstance(time_limit.white_inc, float) else 0
        else:
            my_time = time_limit.black_clock if isinstance(time_limit.black_clock, float) else 0
            my_inc = time_limit.black_inc if isinstance(time_limit.black_inc, float) else 0
        limit = (my_time / 20) + (my_inc / 2)
        engine_path = None
        book_path = None
        return PlayResult(engine.Engine().play(board, limit, engine_path, book_path), None)