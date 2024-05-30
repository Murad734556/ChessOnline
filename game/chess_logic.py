import logging
import os

# Проверка и создание папки для логов
if not os.path.exists("logs/"):
    os.makedirs("logs/")

# Настройка логирования: уровень DEBUG, файл 'chess_logic.log', режим записи 'w' (перезапись),
# формат сообщений: имя, уровень, время и сообщение
logging.basicConfig(level=logging.DEBUG, filename='logs/chess_logic.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(asctime)s %(message)s')
logger = logging.getLogger(__name__)

# Эти переменные будут отслеживать, двигались ли король и ладьи
white_king_moved = False
black_king_moved = False
white_rook_left_moved = False
white_rook_right_moved = False
black_rook_left_moved = False
black_rook_right_moved = False

def get_all_moves(board, piece_pos):
    """
    Возвращает все возможные ходы для фигуры на заданной позиции.
    """
    piece = board[piece_pos[0]][piece_pos[1]]
    all_moves = []
    if piece in [1, 7]:
        # Пешка
        if piece == 1 and board[piece_pos[0]][piece_pos[1] + 1] == 0:
            if piece_pos[1] == 1 and board[piece_pos[0]][piece_pos[1] + 2] == 0:
                move = piece_pos[0], piece_pos[1] + 2
                all_moves.append(move)
            move = piece_pos[0], piece_pos[1] + 1
            all_moves.append(move)
        elif board[piece_pos[0]][piece_pos[1] - 1] == 0:
            if piece_pos[1] == 6:
                move = piece_pos[0], piece_pos[1] - 2
                all_moves.append(move)
            move = piece_pos[0], piece_pos[1] - 1
            all_moves.append(move)
        all_moves.extend(get_pawn_attacks(board, piece_pos, piece))

    elif piece in [2, 8]:
        # Слон
        for i in [1, -1]:
            for j in [1, -1]:
                move = piece_pos[0] + i, piece_pos[1] + j
                if not (is_within_board(move) and is_not_self_piece(board, piece, move)):
                    continue
                for k in range(1, 8):
                    move = piece_pos[0] + i * k, piece_pos[1] + j * k
                    all_moves.append(move)

    elif piece in [3, 9]:
        # Конь
        for i in [1, 2, -1, -2]:
            for j in [1, 2, -1, -2]:
                if abs(i) != abs(j):
                    move = piece_pos[0] + i, piece_pos[1] + j
                    all_moves.append(move)

    elif piece in [4, 10]:
        # Ладья
        for i in [1, -1]:
            for k in range(1, 8):
                move = piece_pos[0] + i * k, piece_pos[1]
                move2 = piece_pos[0], piece_pos[1] - i * k
                all_moves.append(move)
                all_moves.append(move2)

    elif piece in [5, 11]:
        # Ферзь (комбинированные движения слона и ладьи)
        for i in [1, -1]:
            for j in [1, -1]:
                move = piece_pos[0] + i, piece_pos[1] + j
                if not (is_within_board(move) and is_not_self_piece(board, piece, move)):
                    continue
                for k in range(1, 8):
                    move = piece_pos[0] + i * k, piece_pos[1] + j * k
                    all_moves.append(move)
        for i in [1, -1]:
            for k in range(1, 8):
                move = piece_pos[0] + i * k, piece_pos[1]
                move2 = piece_pos[0], piece_pos[1] - i * k
                all_moves.append(move)
                all_moves.append(move2)

    elif piece in [6, 12]:
        # Король
        for i in [1, 0, -1]:
            for j in [1, 0, -1]:
                move = piece_pos[0] + i, piece_pos[1] + j
                all_moves.append(move)

        # Добавление логики рокировки
        if piece == 6:  # Белый король
            if not white_king_moved:
                # Короткая рокировка
                if not white_rook_right_moved and \
                   board[7][5] == 0 and board[7][6] == 0 and \
                   not is_square_under_attack(board, (7, 4), True) and \
                   not is_square_under_attack(board, (7, 5), True) and \
                   not is_square_under_attack(board, (7, 6), True):
                    all_moves.append((7, 6))

                # Длинная рокировка
                if not white_rook_left_moved and \
                   board[7][1] == 0 and board[7][2] == 0 and board[7][3] == 0 and \
                   not is_square_under_attack(board, (7, 2), True) and \
                   not is_square_under_attack(board, (7, 3), True) and \
                   not is_square_under_attack(board, (7, 4), True):
                    all_moves.append((7, 2))
        elif piece == 12:  # Черный король
            if not black_king_moved:
                # Короткая рокировка
                if not black_rook_right_moved and \
                   board[0][5] == 0 and board[0][6] == 0 and \
                   not is_square_under_attack(board, (0, 4), False) and \
                   not is_square_under_attack(board, (0, 5), False) and \
                   not is_square_under_attack(board, (0, 6), False):
                    all_moves.append((0, 6))

                # Длинная рокировка
                if not black_rook_left_moved and \
                   board[0][1] == 0 and board[0][2] == 0 and board[0][3] == 0 and \
                   not is_square_under_attack(board, (0, 2), False) and \
                   not is_square_under_attack(board, (0, 3), False) and \
                   not is_square_under_attack(board, (0, 4), False):
                    all_moves.append((0, 2))

    return all_moves

def is_square_under_attack(board, square, is_white):
    """
    Проверяет, находится ли клетка под атакой вражеской фигуры.
    """
    for x in range(8):
        for y in range(8):
            piece = board[x][y]
            if (is_white and piece > 6) or (not is_white and piece < 7 and piece > 0):
                moves = get_all_moves(board, (x, y))
                for move in moves:
                    if move == square:
                        return True
    return False

def get_pawn_attacks(board, piece_pos, piece):
    """
    Возвращает возможные атаки пешки.
    """
    attacks = []
    if piece == 1:  # Белая пешка
        if 0 <= piece_pos[0] + 1 < 8 and 0 <= piece_pos[1] + 1 < 8 and board[piece_pos[0] + 1][piece_pos[1] + 1] != 0:
            move = piece_pos[0] + 1, piece_pos[1] + 1
            attacks.append(move)
        if 0 <= piece_pos[0] - 1 < 8 and 0 <= piece_pos[1] + 1 < 8 and board[piece_pos[0] - 1][piece_pos[1] + 1] != 0:
            move = piece_pos[0] - 1, piece_pos[1] + 1
            attacks.append(move)
    else:  # Черная пешка
        if 0 <= piece_pos[0] + 1 < 8 and 0 <= piece_pos[1] - 1 < 8 and board[piece_pos[0] + 1][piece_pos[1] - 1] != 0:
            move = piece_pos[0] + 1, piece_pos[1] - 1
            attacks.append(move)
        if 0 <= piece_pos[0] - 1 < 8 and 0 <= piece_pos[1] - 1 < 8 and board[piece_pos[0] - 1][piece_pos[1] - 1] != 0:
            move = piece_pos[0] - 1, piece_pos[1] - 1
            attacks.append(move)
    return attacks

def get_possible_moves(board, all_moves, piece_pos, piece):
    """
    Возвращает возможные ходы фигуры, проверяя их на корректность.
    """
    possible_moves = []
    if piece in [1, 7, 3, 9, 6, 12]:  # Пешка, конь или король
        for move in all_moves:
            logging.debug("[Debug] Проверка для " + str(piece_pos) + "->" + str(move))
            if is_within_board(move) \
                    and is_not_self_piece(board, piece, move):
                possible_moves.append(move)
    else:  # Слон, ладья, ферзь
        for move in all_moves:
            logging.debug("[Debug] Проверка для " + str(piece_pos) + "->" + str(move))
            if is_within_board(move) \
                    and is_not_self_piece(board, piece, move) \
                    and is_not_behind_another_piece(board, piece_pos, move):
                possible_moves.append(move)
    return possible_moves

def check_possible_moves(board, piece_pos):
    """
    Возвращает ходы, которые не приводят к шаху своему королю.
    """
    not_checkmate_moves = []
    piece = board[piece_pos[0]][piece_pos[1]]
    all_moves = get_all_moves(board, piece_pos)
    possible_moves = get_possible_moves(board, all_moves, piece_pos, piece)

    for move in possible_moves:
        if is_not_giving_checkmate(board, piece_pos, piece, move):
            not_checkmate_moves.append(move)
    return not_checkmate_moves

def is_within_board(move):
    """
    Проверяет, находится ли ход внутри доски.
    """
    is_within = not (move[0] < 0 or move[0] > 7 or move[1] < 0 or move[1] > 7)
    logging.debug(str(move[0]) + "," + str(move[1]) + " внутри доски: " + str(is_within))
    return is_within

def is_not_self_piece(board, piece, move):
    """
    Проверяет, не является ли клетка занята своей фигурой.
    """
    is_not_self = True
    if board[move[0]][move[1]] == 0:
        logging.debug(str(move[0]) + "," + str(move[1]) + " не своя фигура: " + str(is_not_self))
        return is_not_self
    elif piece < 7:
        is_not_self = board[move[0]][move[1]] >= 7
    else:
        is_not_self = board[move[0]][move[1]] <= 6

    logging.debug(str(move[0]) + "," + str(move[1]) + " не своя фигура: " + str(is_not_self))
    return is_not_self

def is_not_behind_another_piece(board, piece_pos, move):
    """
    Проверяет, не находится ли фигура за другой фигурой.
    """
    diff_x = piece_pos[0] - move[0]
    diff_y = piece_pos[1] - move[1]
    temp_x = piece_pos[0]
    temp_y = piece_pos[1]
    is_behind = True
    
    while diff_x != 0 or diff_y != 0:
        if diff_x > 0:
            diff_x -= 1
            temp_x -= 1
        elif diff_x < 0:
            diff_x += 1
            temp_x += 1

        if diff_y > 0:
            diff_y -= 1
            temp_y -= 1
        elif diff_y < 0:
            diff_y += 1
            temp_y += 1

        if board[temp_x][temp_y] != 0 and move != (temp_x, temp_y):
            is_behind = False
            logging.debug(str(move[0]) + "," + str(move[1]) + " не за другой фигурой: " + str(is_behind))
            break
    logging.debug(str(move[0]) + "," + str(move[1]) + " не за другой фигурой: " + str(is_behind))
    return is_behind

def is_not_giving_checkmate(board, piece_pos, piece, move):
    """
    Проверяет, не приводит ли ход к шаху своему королю.
    """
    pieces_to_check = []
    king_pos = []
    for x_index in range(0, 8):
        for y_index in range(0, 8):
            if piece < 7:
                if board[x_index][y_index] < 7:
                    if board[x_index][y_index] == 6:
                        king_pos = [x_index, y_index]
                    continue
            else:
                if board[x_index][y_index] > 6 or board[x_index][y_index] == 0:
                    if board[x_index][y_index] == 12:
                        king_pos = [x_index, y_index]
                    continue
            pieces_to_check.append([x_index, y_index])
    if piece in [6, 12]:
        king_pos = [move[0], move[1]]
    
    # Имитация движения
    temp_board = [row[:] for row in board]
    temp_board[piece_pos[0]][piece_pos[1]] = 0
    temp_board[move[0]][move[1]] = piece

    for enemy_piece_pos in pieces_to_check:
        enemy_piece = temp_board[enemy_piece_pos[0]][enemy_piece_pos[1]]
        enemy_moves = get_all_moves(temp_board, enemy_piece_pos)
        enemy_possible_moves = get_possible_moves(temp_board, enemy_moves, enemy_piece_pos, enemy_piece)
        if (king_pos[0], king_pos[1]) in enemy_possible_moves:
            logging.debug(str(move[0]) + "," + str(move[1]) + " ставит шах королю")
            return False
    logging.debug(str(move[0]) + "," + str(move[1]) + " не ставит шах королю")
    return True

def is_checkmate(board, is_white):
    """
    Проверяет, находится ли король под матом.
    """
    ally_pieces = []
    for x_index in range(0, 8):
        for y_index in range(0, 8):
            if is_white:
                if 7 > board[x_index][y_index] > 0:
                    ally_pieces.append([x_index, y_index])
                else:
                    continue
            else:
                if board[x_index][y_index] > 6:
                    ally_pieces.append([x_index, y_index])

    for ally_piece_pos in ally_pieces:
        ally_possible_moves = check_possible_moves(board, ally_piece_pos)
        if ally_possible_moves:
            return False
    return True
