import pygame, pygame_menu, threading
from game.board import black
from network_client import Client

pygame.init()

# Размеры окна игры
size = width, height = 600, 800
board_size = 600, 600
field_board_size = 5

# Создание окна игры
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Chess Client')
screen.fill(black)

def start_game(name, server_ip, server_port):
    """
    Функция для начала игры. Подключается к серверу игры и обновляет статус подключения.
    
    :param name: имя игрока
    :param server_ip: IP адрес сервера
    :param server_port: порт сервера
    """
    game_client = Client(name, server_ip, int(server_port))
    menu.get_widget("is_connecting").set_title("Connecting...")
    menu.close()
    if game_client.connected:
        menu.get_widget("is_connecting").set_title("Connected")
        menu.close()
    else:
        menu.get_widget("is_connecting").set_title("Couldn't connect to a game server..")

def join_the_game():
    """
    Функция для получения данных от виджетов меню и начала игры.
    """
    name = menu.get_widget('name').get_value()
    server_ip = menu.get_widget('server_ip').get_value()
    server_port = menu.get_widget('server_port').get_value()
    menu.get_widget("is_connecting").set_title("Connecting...")
    start_game(name, server_ip, server_port)

# Создание меню
menu = pygame_menu.Menu('Chess Game', 600, 800,
                        theme=pygame_menu.themes.THEME_DARK)
# Добавление текстовых полей и кнопок в меню
menu.add.text_input('Name: ', default='Игрок', textinput_id="name")
menu.add.text_input('Server IP: ', default='127.0.0.1', textinput_id="server_ip")
menu.add.text_input('Port: ', default='12395', textinput_id="server_port")
menu.add.button('Join', join_the_game)
menu.add.button('Quit', pygame_menu.events.PYGAME_QUIT)
menu.add.label("", label_id="is_connecting")

# Запуск меню
menu.mainloop(screen)

