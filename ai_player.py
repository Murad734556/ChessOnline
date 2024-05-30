import chess
import chess.engine

def get_ai_move(board):
    with chess.engine.SimpleEngine.popen_uci("/path/to/stockfish") as engine:
        result = engine.play(board, chess.engine.Limit(time=0.1))
        return result.move
