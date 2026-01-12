from stockfish import Stockfish

stockfish = Stockfish(path="stockfish-src/stockfish-ubuntu-x86-64")

stockfish.update_engine_parameters({"UCI_Elo": 2048}) # Gets stockfish to use a 2GB hash table, and also to play Chess960.


stockfish.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")

print("is fen validL ", stockfish.is_fen_valid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"))


print("best move ", stockfish.get_best_move())

print("topk moves", stockfish.get_top_moves(3))

print(stockfish.get_wdl_stats())

print(stockfish.get_parameters())

print(stockfish.get_evaluation())


print(stockfish.get_stockfish_major_version())