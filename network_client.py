import socket
import select
from network_tools import encode_flag_data, decode_flag_data
import pygame, sys
from pygame.locals import *
from game.board import Board, black


class Client:
    def __init__(self, name, serv_ip, port=65432):
        self.size = self.width, self.height = 600, 800
        self.board_size = 600, 600
        self.field_board_size = 5
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption('Chess Client')
        self.screen.fill(black)

        self.name = name
        self.enemy_name = None
        self.game = False
        self.is_white = False

        try:
            self.connfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connfd.connect((serv_ip, port))
            self.connfd.sendall(self.name.encode())
            self.mydata = self.name, self.connfd.getsockname()[0], self.connfd.getsockname()[1]
        except socket.error as e:
            print(f'An error has occurred while creating socket: {e}')
            return
        print('Connected to server!')

        self.main_loop()

    def main_loop(self):
        # game window
        pygame.init()

        board = Board(self.screen, self.board_size, self.field_board_size)
        board.draw_board_background()
        board.draw_pieces()
        self._print_info("В ожидании игрока..")

        while True:
            infds, outfds, errfds = select.select([self.connfd], [self.connfd], [], 10)
            if len(infds) != 0:
                msg = self.connfd.recv(1024)
                if not msg:
                    print('kappa')
                    break
                flag, data = decode_flag_data(msg)
                print(flag, data)
                if flag == 'gs':
                    print('Игра началась!')
                    self.game = True

                    """         
                    [sp] - starting packet - (color, enemy name)
                    [ap] - active player
                    [bs] - board status
                    [im] - incorrect move
                    [go] - game over -> CHECKMATE
                    [gs] - game staus
                    [mv] - move
                    """
                elif flag == 'sp':
                    self.is_white = data[0]
                    self.enemy_name = str(data[1][0])
                elif flag == 'ap':
                    if self.mydata == data:
                        print('Ваш ход!')
                        board.draw_board_background()
                        board.draw_pieces()
                        self._print_info("Ваш ход..")
                        self._print_status()
                        not_moved = True
                        while not_moved:
                            events = pygame.event.get()
                            for event in events:
                                if event.type == pygame.QUIT: sys.exit()
                                if event.type == MOUSEBUTTONDOWN:
                                    if event.button == 1:
                                        move = board.handle_mouse_click(event.pos)
                                        if move:
                                            self.connfd.sendall(encode_flag_data('mv', move))
                                            not_moved = False
                            pygame.display.flip()
                    else:
                        print('Пожалуйста, подождите, пока второй игрок сделает ход.')
                        board.draw_board_background()
                        board.draw_pieces()
                        self._print_info("Пожалуйста, подождите, пока второй игрок сделает ход.")
                        self._print_status()
                elif flag == 'bs':
                    board.board = data
                    board.draw_board_background()
                    board.draw_pieces()
                    self._print_info("Updating board..")
                    self._print_status()
                    pass
                elif flag == 'im':
                    board.draw_board_background()
                    board.draw_pieces()
                    self._print_info("Неправильный ход!")
                    self._print_status()
                elif flag == 'go':
                    if data:
                        self._print_info("CHECKMATE! \n Вы победили!")
                    else:
                        self._print_info("CHECKMATE! \n Вы проиграли..")

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: sys.exit()
            pygame.display.flip()

        self.connfd.close()

    def _print_info(self, text):
        myfont = pygame.font.SysFont("monospace", 15)
        label_text = text
        label = myfont.render(label_text, 1, (255, 255, 255))
        label_rect = label.get_rect(
            center=(self.width / 2, self.board_size[1] + (self.height - self.board_size[1]) / 2))
        self.screen.blit(label, label_rect)

    def _print_status(self):
        myfont = pygame.font.SysFont("monospace", 15)
        if self.is_white:
            label_text = "[WHITE] PLAYER vs " + self.enemy_name + " [BLACK]"
        else:
            label_text = "[BLACK] PLAYER vs " + self.enemy_name + " [WHITE]"

        label = myfont.render(label_text, 1, (255, 255, 255))
        label_rect = label.get_rect(
            center=(self.width / 2, self.board_size[1] + 50))
        self.screen.blit(label, label_rect)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Arguments: [name], [server_ip_address], [server_port](default 65432)')
    elif len(sys.argv) == 3:
        Client(sys.argv[1], sys.argv[2])
    else:
        try:
            Client(sys.argv[1], sys.argv[2], int(sys.argv[3]))
        except ValueError:
            print("Invalid port number!")
