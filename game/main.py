import pygame, sys, os
from pygame.locals import *
from board import Board, black

# Инициализация Pygame
pygame.init()

# Установка размеров окна
size = width, height = 600, 650
board_size = 600, 600
field_board_size = 5

# Создание окна приложения
screen = pygame.display.set_mode(size)

# Создание объекта доски
board = Board(screen, board_size, field_board_size)
screen.fill(black)  # Заполнение фона черным цветом
board.draw_board_background()  # Отрисовка фона доски
board.draw_pieces()  # Отрисовка фигур на доске

# Основной цикл приложения
while 1:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Если событие - выход, закрываем приложение
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:  # Если событие - нажатие кнопки мыши
            if event.button == 1:  # Если нажата левая кнопка мыши
                board.handle_mouse_click(event.pos)  # Обработка нажатия на доску

    pygame.display.flip()  # Обновление экрана
