import socket
import threading
import sys
import time
import random
from network_tools import encode_flag_data, decode_flag_data
from game.board_server import Board


def handle_game(player_one, player_one_connfd: socket.socket, player_two, player_two_connfd: socket.socket):
    """
    основная функция, которая занимается конкретной игрой, запускается как частный поток и принимает данные от игроков или
    декскрипторы их гнезд в качестве аргументов

    сделать комуникование, если у вас есть клиенты, которые используют флаг и начальные функции, которые делают есвятланию флаги + даныч
    вы можете отправлять любые типы данных, которые можно записать в функцию Pickle.dumps().

    для преобразования флагов + сообщений/данных в байты, которые можно отправить, можно использовать функцию confd.sendall()
    функция encode_flag_data('flag', data), она возвращает сообщение в байтовой форме, готовое к отправке

    чтобы отключить процесс, вы можете использовать функцию decode_flag_data(msg), которая использует сообщение в качестве аргумента
    удаляется с помощью connfd.recv() и возвращает данные в виде кроток (флаг, данные)

    :param player_one:
    :param player_one_connfd:
    :param player_two:
    :param player_two_connfd:
    :return:
    """
    game_board = Board()
    try:
        game = True
        # отправка обоим игрокам информации о том, что игра начинается (это позволит им выйти из бесконечного цикла
        try:
            player_one_connfd.sendall(encode_flag_data('gs', ''))
            player_two_connfd.sendall(encode_flag_data('gs', ''))
        except OSError:
            player_one_connfd.close()
            player_two_connfd.close()
            return
        time.sleep(1)

        # ustawienie aktywnego gracza oraz deksryptora jego gniazda
        # DONE: można dodać losowanie kto zaczyna
        if random.choice([player_one, player_two]) == player_one:
            active_player = player_one
            active_player_connfd = player_one_connfd
            black_player_connfd = player_two_connfd
            white_player_connfd = active_player_connfd
            try:
                white_player_connfd.sendall(encode_flag_data('sp', [True,  player_two]))
                black_player_connfd.sendall(encode_flag_data('sp', [False, player_one]))
            except OSError:
                player_one_connfd.close()
                player_two_connfd.close()
                return
        else:
            active_player = player_two
            active_player_connfd = player_two_connfd
            black_player_connfd = player_one_connfd
            white_player_connfd = active_player_connfd
            try:
                white_player_connfd.sendall(encode_flag_data('sp', [True,  player_one]))
                black_player_connfd.sendall(encode_flag_data('sp', [False, player_two]))
            except OSError:
                player_one_connfd.close()
                player_two_connfd.close()
                return

        is_checkmate = False
        white_won = False
        time.sleep(1)

        while game:
            """
            как показано ниже, лучше всего реализовать отправку сообщений игрокам и получение сообщений от активных игроков.
            игрок, в этом случае информация об активном игроке отправляется (флаг 'ap' - активный игрок) после
            после чего активный игрок ждет хода
            """
            if is_checkmate:
                if white_won:
                    try:
                        white_player_connfd.sendall(encode_flag_data('go', True))
                        black_player_connfd.sendall(encode_flag_data('go', False))
                    except OSError:
                        player_one_connfd.close()
                        player_two_connfd.close()
                        return
                else:
                    try:
                        black_player_connfd.sendall(encode_flag_data('go', True))
                        white_player_connfd.sendall(encode_flag_data('go', False))
                    except OSError:
                        player_one_connfd.close()
                        player_two_connfd.close()
                        return
                game = False
                break

            try:
                player_one_connfd.sendall(encode_flag_data('ap', active_player))
                player_two_connfd.sendall(encode_flag_data('ap', active_player))
            except OSError:
                player_one_connfd.close()
                player_two_connfd.close()
                return
            msg = active_player_connfd.recv(1024)

            flag, data = decode_flag_data(msg)
            print(flag, data)

            """
            tutaj powinna być logika gry (sprwadzanie ruchów, wysyłanie stanu planszy do graczy, wysyłanie
            informacji o stanie gry
            """

            if flag == 'mv':

                is_move_correct = game_board.move_piece(data[0], data[1], active_player_connfd == white_player_connfd)

                if is_move_correct:
                    try:
                        player_one_connfd.sendall(encode_flag_data('bs', game_board.board))
                        player_two_connfd.sendall(encode_flag_data('bs', game_board.board))
                    except OSError:
                        player_one_connfd.close()
                        player_two_connfd.close()
                        return

                    is_checkmate = game_board.check_checkmate(active_player_connfd == white_player_connfd)
                    if is_checkmate:
                        if active_player_connfd == white_player_connfd:
                            white_won = True
                        else:
                            white_won = False
                    time.sleep(1)
                else:
                    try:
                        active_player_connfd.sendall(encode_flag_data('im', "move not possible!"))
                    except OSError:
                        player_one_connfd.close()
                        player_two_connfd.close()
                        return
                    time.sleep(1)
                    continue

            # zmiana aktywnego gracza, te dwie linijki powinny zostać na końcu tej pętli
            active_player = player_one if active_player == player_two else player_two
            active_player_connfd = player_one_connfd if active_player_connfd == player_two_connfd else player_two_connfd
    except BrokenPipeError as e:
        print(f'Error has occurred: {e}')
        try:
            player_one_connfd.close()
            player_two_connfd.close()
        except:
            print('Error has occurred while closing sockets')


class Server:
    def __init__(self, ip='', port=65432):
        self.clients_connected = {}
        self.ip = ip
        self.port = port
        self.keep_track = True

        try:
            self.listenfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listenfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listenfd.bind((self.ip, self.port))
            self.listenfd.listen(4)
        except socket.error as e:
            print(f'An error has occurred: {e}')
            return
        print(f'Server is running.')

        self.main_loop()

    def check_client_connection(self, connfd: socket.socket, client_data):
        connfd.settimeout(0.1)
        while self.keep_track:
            try:
                msg = connfd.recv(1024)
                if not msg:
                    print(f'Client {client_data} disconnected.')
                    if client_data in self.clients_connected.keys():
                        self.clients_connected.pop(client_data)
                    connfd.close()
                break
            except socket.timeout as e:
                pass
            except socket.error as e:
                print("Error has occurred!")
                return

        connfd.settimeout(100000)

    def main_loop(self):
        while True:
            while len(self.clients_connected) < 2:
                connfd, cli_addr = self.listenfd.accept()

                name = connfd.recv(1024)
                name = name.decode()

                client_data = (name, cli_addr[0], cli_addr[1])

                if len(self.clients_connected) == 0:
                    connfd.sendall(encode_flag_data('ms', 'Waiting for other player...'))

                print(f'{client_data} connected.')

                self.clients_connected[client_data] = connfd

                thread = threading.Thread(target=self.check_client_connection, args=[connfd, client_data])
                thread.start()

            self.keep_track = False
            time.sleep(1)

            player_one = list(self.clients_connected.keys())[0]
            player_two = list(self.clients_connected.keys())[1]
            player_one_connfd = self.clients_connected.pop(player_one)
            player_two_connfd = self.clients_connected.pop(player_two)

            threading.Thread(target=handle_game,
                             args=[player_one, player_one_connfd, player_two, player_two_connfd]).start()

            self.keep_track = True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Arguments: [server_ip_address], [server_port](default 65432)')
    elif len(sys.argv) == 2:
        Server(sys.argv[1])
    else:
        try:
            Server(sys.argv[1], int(sys.argv[2]))
        except ValueError:
            print("Invalid port number!")
