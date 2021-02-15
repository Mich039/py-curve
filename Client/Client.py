from enum import Enum
import pygame as pg
from GameObjects.Input import PlayerInput, PlayerLobbyInput
from Socket.client import Client

STATES = Enum("States", "menu lobby ingame")
currentState = STATES.menu
lobby: PlayerLobbyInput = None
client: Client = None

IP = "127.0.0.1"
PORT = 4321
WIDTH = 1000
HEIGHT = 1000
BASE_SPEED = 1.0
WINDOW = pg.display.set_mode((WIDTH, HEIGHT))


pg.display.set_caption("Client")

clientNumber = 0

def init_client():
    global client
    client = Client(IP, PORT, 'test_1')
    client.start()

def set_state(state):
    global currentState
    currentState = state

def join(id: int):
    if id < 0: return
    lobby = PlayerLobbyInput.PlayerLobbyInput()
    lobby.create_new_lobby = False
    lobby.lobby_id = id
    client.say(lobby)
    set_state(STATES.lobby)

def render_waiting_for_start():
    WINDOW.fill((30, 30, 30))
    blue = (0, 0, 128)
    green = (0, 255, 0)
    font = pg.font.Font(None, 32)
    text = font.render('Waiting For Start', True, green, blue)
    textRect = text.get_rect()
    textRect.center = (WIDTH // 2, HEIGHT // 2)
    WINDOW.blit(text, textRect)


def render_menu():
    font = pg.font.Font(None, 32)
    clock = pg.time.Clock()
    input_box = pg.Rect(100, 100, 140, 32)
    color_inactive = pg.Color('lightskyblue3')
    color_active = pg.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive
            if event.type == pg.KEYDOWN:
                if active:
                    if event.key == pg.K_RETURN:
                        join((int)(text))
                        return
                        text = ''
                    elif event.key == pg.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        WINDOW.fill((30, 30, 30))
        # Render the current text.
        txt_surface = font.render(text, True, color)
        # Resize the box if the text is too long.
        width = max(60, txt_surface.get_width()+10)
        input_box.w = width
        # Blit the text.
        WINDOW.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input_box rect.
        pg.draw.rect(WINDOW, color, input_box, 2)
        pg.display.flip()


if __name__ == '__main__':
    init_client()

    clock = pg.time.Clock()
    pg.init()
    while(1):
        if currentState == STATES.menu:
            render_menu()
        if currentState == STATES.lobby:
            render_waiting_for_start()
            #global client
            #client.
        if currentState == STATES.ingame:
            pass
        clock.tick(100)
        pg.display.update()
    pg.quit()