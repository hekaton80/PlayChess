from .chessboard import Chessboard
from ..config import Worker

clry = Worker.worker

class Puzzle:
    def __init__(self, puzzle_obj):
        self._id = puzzle_obj['_id']
        self.attemps = puzzle_obj['attempts']
        self.solved = puzzle_obj['solved']
        self.rating = puzzle_obj['rating']
        self.public = puzzle_obj['public']
        self.start_pos = puzzle_obj['start_pos']
        self.solution = puzzle_obj['solution']
        self.moves = 0
        self.tags = puzzle_obj['tags']
        self.board = Chessboard(puzzle_obj['start_pos'])

    def get_board(self):
        return self.board.draw_chessboard_for_white()

    def generate_legal_moves(self, initial_pos):
        return self.board.generate_legal_moves(initial_pos)

    def make_move(self, initial_pos, final_pos, dest_piece=None):
        res = { 'changes': [], 'success': False, 'puzzleOver': False }
        notation = initial_pos + "-" + final_pos if dest_piece is None else initial_pos + "-" + final_pos + "-" + dest_piece

        if self.moves < len(self.solution) and self.solution[self.moves] ==  notation:
            res['success'] = True
            self.moves += 1
            res['changes'] += self.board.make_move(initial_pos, final_pos, dest_piece=dest_piece)
            if self.moves < len(self.solution):
                squares = self.solution[self.moves].split('-')
                dest_square = squares[2] if len(squares)==3 else None
                res['changes'] += self.board.make_move(squares[0], squares[1], dest_piece=dest_square)
                self.moves += 1
            else:
                res['puzzleOver'] = True

            return res
            
        res['changes'] += self.board.make_move(initial_pos, final_pos, dest_piece=dest_piece)
        return res

    def get_score(self):
        return self.moves / len(self.solution)

def pushPuzzleResult(db_object, puzzle_id, username, result):
    db_object.puzzle.update_one(
        {'_id': puzzle_id},
        {'$inc': {
            "attempts": 1,
            "solved": result,
        }}
    )
    db_object.users.update_one(
        {'username': username},
        {"$push": {"puzzles": {
                "_id" : puzzle_id,
                "score": result,
            }
        }}
    )

def addTag(db_object, puzzle_id, tag):
    db_object.update_one(
        {'_id': puzzle_id},
        {"$push": {'tags': tag}},
    )

def createPuzzle(db_object, start_pos, solution, tags=[]):
    insert_id = db_object.puzzle.insert_one({
        'attempts': 0,
        'solved': 0,
        'rating': 1200,
        'public': False,
        'start_pos': start_pos,
        'solution': solution,
        'tags': tags
    })
    return insert_id

def fetch_puzzle(db_object, puzzle_id):
    puzzle = db_object.puzzle.find_one(
        {'_id': puzzle_id}
    )
    return Puzzle(puzzle)