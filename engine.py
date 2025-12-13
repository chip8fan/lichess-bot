import chess
import chess.engine
import chess.polyglot
class Engine():
    def play(self, board, max_time, engine_path, book_path):
        try:
            with chess.polyglot.open_reader(book_path) as reader:
                self.move = reader.choice(board).move
        except IndexError:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
            self.move = self.engine.play(board, chess.engine.Limit(time=max_time)).move
            self.engine.quit()
        return self.move