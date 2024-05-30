import unittest
from chess_logic import (
    check_possible_moves,
    is_checkmate,
    is_within_board,
    is_not_self_piece,
    is_not_behind_another_piece,
    is_square_under_attack,
    is_not_giving_checkmate
)


class TestChessLogic(unittest.TestCase):

    def setUp(self):
        self.board = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def test_square_under_attack_by_white(self):
        self.board[3][3] = 11
        square = (3, 6)

        self.assertTrue(is_square_under_attack(self.board, square, is_white=True))

    def test_square_not_under_attack_by_white(self):
        self.board[3][3] = 11
        square = (5, 5)

        self.assertFalse(is_square_under_attack(self.board, square, is_white=False))

    def test_square_under_attack_by_black(self):
        self.board[3][3] = 5
        square = (3, 6)

        self.assertTrue(is_square_under_attack(self.board, square, is_white=False))

    def test_square_not_under_attack_by_black(self):
        self.board[3][3] = 5
        square = (5, 5)

        self.assertFalse(is_square_under_attack(self.board, square, is_white=True))

    def test_check_possible_moves(self):
        board = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        piece_pos = (4, 3)
        result = check_possible_moves(board, piece_pos)
        self.assertEqual(len(result), 1)
        self.assertIn((4, 4), result)

    def test_is_within_board(self):
        move_inside_1 = (3, 4)
        move_inside_2 = (2, 7)
        move_inside_3 = (4, 2)
        self.assertTrue(is_within_board(move_inside_1))
        self.assertTrue(is_within_board(move_inside_2))
        self.assertTrue(is_within_board(move_inside_3))

        move_outside_1 = (8, 9)
        move_outside_2 = (11, 10)
        move_outside_3 = (12, 13)
        self.assertFalse(is_within_board(move_outside_1))
        self.assertFalse(is_within_board(move_outside_2))
        self.assertFalse(is_within_board(move_outside_3))

    def test_is_not_self_piece(self):
        board = [
            [1, 0, 0, 0, 0, 0, 0, 7],
            [0, 2, 0, 0, 0, 0, 8, 0],
            [0, 0, 3, 0, 0, 9, 0, 0],
            [0, 0, 0, 4, 10, 0, 0, 0],
            [0, 0, 0, 0, 5, 0, 0, 0],
            [0, 0, 0, 0, 0, 6, 0, 0],
            [0, 0, 0, 0, 0, 0, 11, 0],
            [0, 0, 0, 0, 0, 0, 0, 12]
        ]

        move_empty = (0, 1)
        piece = 1
        self.assertTrue(is_not_self_piece(board, piece, move_empty))

        move_self_white = (0, 0)
        piece_white = 1
        self.assertFalse(is_not_self_piece(board, piece_white, move_self_white))

        move_self_black = (7, 7)
        piece_black = 7
        self.assertFalse(is_not_self_piece(board, piece_black, move_self_black))

        move_opponent_black = (0, 7)
        self.assertTrue(is_not_self_piece(board, piece_white, move_opponent_black))

        move_opponent_white = (7, 0)
        self.assertTrue(is_not_self_piece(board, piece_black, move_opponent_white))

    def test_is_not_behind_another_piece(self):
        board = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

        piece_pos = (2, 2)

        move_not_behind = (4, 2)
        self.assertTrue(is_not_behind_another_piece(board, piece_pos, move_not_behind))

        board[3][2] = 2
        move_behind_vertical = (4, 2)
        self.assertFalse(is_not_behind_another_piece(board, piece_pos, move_behind_vertical))

        board[3][2] = 0
        move_not_behind_diagonal = (4, 4)
        self.assertTrue(is_not_behind_another_piece(board, piece_pos, move_not_behind_diagonal))

        board[3][3] = 2
        move_behind_diagonal = (4, 4)
        self.assertFalse(is_not_behind_another_piece(board, piece_pos, move_behind_diagonal))

        move_not_behind_horizontal = (2, 5)
        self.assertTrue(is_not_behind_another_piece(board, piece_pos, move_not_behind_horizontal))

        board[2][4] = 2
        move_behind_horizontal = (2, 5)
        self.assertFalse(is_not_behind_another_piece(board, piece_pos, move_behind_horizontal))

    def test_move_not_giving_checkmate(self):

        self.board[4][4] = 6
        self.board[3][3] = 1
        piece_pos = (3, 3)
        move = (3, 4)
        piece = 1

        self.assertTrue(is_not_giving_checkmate(self.board, piece_pos, piece, move))

    def test_king_move_not_giving_checkmate(self):

        self.board[4][4] = 6
        piece_pos = (4, 4)
        move = (4, 5)
        piece = 6

        self.assertTrue(is_not_giving_checkmate(self.board, piece_pos, piece, move))


    def test_is_checkmate(self):
        board = [
            [4, 0, 0, 0, 0, 0, 0, 4],  # Ладьи черные
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 6, 0, 0, 0],  # Белый король
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]   # Ладьи отсутствуют
        ]
        self.assertFalse(is_checkmate(board, is_white=True))

        board = [
            [4, 0, 0, 0, 12, 0, 0, 4],  # Ладьи черные и черный король
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 6, 0, 0, 0],   # Белый король
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]   # Ладьи отсутствуют
        ]
        self.assertFalse(is_checkmate(board, is_white=False))


if __name__ == '__main__':
    unittest.main()
import unittest