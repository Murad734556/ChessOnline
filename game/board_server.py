import pygame
import os
from .chess_logic import check_possible_moves, is_checkmate

# Определение цветов
black = 0, 0, 0
white = 255, 255, 255
floralwhite = 255, 250, 240
grey = 192, 192, 192
ivory = 255, 255, 15
limegreen = 50, 205, 50

class Board:
    def __init__(self):
        """
        Инициализация объекта доски. Устанавливает начальное состояние доски и переменные для управления ходами.
        """
        self.board = self.default_board()
        self.possible_moves = []
        self.field_selected = 0, 0

    def default_board(self):
        """
        Создание стартовой позиции шахматной доски.

        :return: начальная позиция доски
        """
        board = [[0 for i in range(8)] for i in range(8)]
        for a in range(8):
            board[a][1] = 1  # черные пешки
            board[a][6] = 7  # белые пешки

        # Расстановка остальных фигур
        board[0][0] = 4
        board[7][0] = 4
        board[1][0] = 3
        board[6][0] = 3
        board[2][0] = 2
        board[5][0] = 2
        board[3][0] = 5
        board[4][0] = 6

        board[0][7] = 10
        board[7][7] = 10
        board[1][7] = 9
        board[6][7] = 9
        board[2][7] = 8
        board[5][7] = 8
        board[3][7] = 11
        board[4][7] = 12

        return board

    def move_piece(self, previous_field, field, is_white):
        """
        Обрабатывает движение фигуры на доске.

        :param previous_field: начальная позиция фигуры
        :param field: конечная позиция фигуры
        :param is_white: True, если ход делает белый игрок, False для черного
        :return: True, если ход выполнен успешно, иначе False
        """
        self.field_selected = previous_field

        # Проверка, что ходит правильная фигура (белая или черная)
        if is_white and self.board[previous_field[0]][previous_field[1]] < 7:
            return False
        if not is_white and self.board[previous_field[0]][previous_field[1]] >= 7:
            return False

        # Получение всех возможных ходов для выбранной фигуры
        possible_moves = []
        for possible_field in check_possible_moves(self.board, self.field_selected):
            possible_moves.append(possible_field)

        # Проверка, что ход валиден
        if field == self.field_selected or field not in possible_moves:
            return False

        # Если ход валиден, выполняем его
        else:
            past_piece = self.board[self.field_selected[0]][self.field_selected[1]]
            self.board[field[0]][field[1]] = past_piece
            self.board[self.field_selected[0]][self.field_selected[1]] = 0

            # Обработка рокировки
            if past_piece in [6, 12]:  # Если это король
                if is_white:
                    white_king_moved = True
                    if field == (7, 6):  # Короткая рокировка белых
                        self.board[7][5] = 10  # Перемещаем ладью
                        self.board[7][7] = 0  # Очищаем старую позицию ладьи
                        white_rook_right_moved = True
                    elif field == (7, 2):  # Длинная рокировка белых
                        self.board[7][3] = 10  # Перемещаем ладью
                        self.board[7][0] = 0  # Очищаем старую позицию ладьи
                        white_rook_left_moved = True
                else:
                    black_king_moved = True
                    if field == (0, 6):  # Короткая рокировка черных
                        self.board[0][5] = 4  # Перемещаем ладью
                        self.board[0][7] = 0  # Очищаем старую позицию ладьи
                        black_rook_right_moved = True
                    elif field == (0, 2):  # Длинная рокировка черных
                        self.board[0][3] = 4  # Перемещаем ладью
                        self.board[0][0] = 0  # Очищаем старую позицию ладьи
                        black_rook_left_moved = True

            return True

    def check_checkmate(self, is_white):
        """
        Проверяет, находится ли текущий игрок в состоянии мата.

        :param is_white: True, если проверка для белых, False для черных
        :return: True, если мат, иначе False
        """
        return is_checkmate(self.board, is_white)
