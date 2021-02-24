from enum import Enum
import pygame as pg

from Client import ClientConstants
from GameObjects.Input import PlayerInput, PlayerLobbyInput
from GameObjects import GameState, PlayerStatus
from GameObjects.LobbyState import LobbyState
from Socket.client import Client

IP = "192.168.100.11"
PORT = 4321
WIDTH = 1000
HEIGHT = 1000
BASE_SPEED = 1.0

RED = (255, 0, 0)
GREEN = (0, 255, 0)


pg.display.set_caption("Client")


def _points_to_tuples(points):
    res = []
    for p in points:
        res.append((p.x, p.y))
    return res


class GameClient:

    def __init__(self):
        self._game_state: GameState = None
        self._client: Client = None
        self._player_id: str = None
        self._window = pg.display.set_mode((WIDTH, HEIGHT))
        self._force_wait = False
        self._last_input = None

    def init_client(self, ip=IP, port=PORT, name="User"):
        self._client = Client(ip, port, name)
        self._client.receive_message_event = self._handle_game_state
        print("init client done")

    def join(self, id: int):
        self._force_wait = True
        if id < 0:
            lobby = PlayerLobbyInput.PlayerLobbyInput()
            lobby.create_new_lobby = True
            self._client.say(lobby)
        else:
            lobby = PlayerLobbyInput.PlayerLobbyInput()
            lobby.create_new_lobby = False
            lobby.lobby_id = id
            self._client.say(lobby)

    def test(self):
        self._window.fill((30, 30, 30))
        blue = (0, 0, 128)
        green = (0, 255, 0)
        font = pg.font.Font(None, 32)
        text = font.render('Waiting For Start', True, green, blue)
        textRect = text.get_rect()
        textRect.center = (WIDTH // 2, HEIGHT // 2)
        self._window.blit(text, textRect)
        for event in pg.event.get():
            print(event)
    # toggle ready

    def _render_between_rounds(self):
        text_recs = []
        texts = []
        font = pg.font.Font(None, 32)

        self._window.fill(ClientConstants.BACKGROUND_COLOR)

        h = font.render("--- Score ---", True, (255, 0, 0))
        hr = h.get_rect()
        hr.center = (WIDTH // 2, 100)
        self._window.blit(h, hr)

        count = 0
        ready_state = False
        for player in self._game_state.player_list:
            count = count + 1
            color = player.color
            if player.id == self._player_id:
                if player.player_status == PlayerStatus.PlayerStatus.READY:
                    ready_state = True
                font.set_italic(True)
            else:
                font.set_italic(False)
            t = font.render(f'P{count}: {player.score.score_points}', True, color)
            tr = t.get_rect()
            tr.center = (WIDTH // 2, 200 + 20 * count)
            text_recs.append(tr)
            texts.append(t)

        font.set_italic(False)
        if ready_state:
            t = font.render('Ready', True, GREEN)
        else:
            t = font.render('Not Ready', True, RED)
        tr = t.get_rect()
        tr.center = (WIDTH // 2, HEIGHT - 50)
        text_recs.append(tr)
        texts.append(t)

        for i in range(len(texts)):
            self._window.blit(texts[i], text_recs[i])

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                input = PlayerInput.PlayerInput()
                if event.key == pg.K_SPACE:
                    input.space = True
                self._client.say(input)

    def _render_game(self):
        self._window.fill(ClientConstants.BACKGROUND_COLOR)
        for player in self._game_state.player_list:
            for sublist in player.body:
                if len(sublist) < 2:
                    continue
                sublist = _points_to_tuples(sublist)
                pg.draw.lines(self._window, player.color, points=sublist, closed=False, width=3)
            pg.draw.circle(self._window, (255, 255, 0), (player.head.x, player.head.y), 3)

        if self._game_state.ground_power_up:
            for power_up in self._game_state.ground_power_up:
                pg.draw.circle(self._window, ClientConstants.POWER_UP_COLORS[power_up.power_up_type], power_up.location, 5)


        for event in pg.event.get():
            input = PlayerInput.PlayerInput()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    input.left = True
                elif event.key == pg.K_RIGHT:
                    input.right = True
            if not self._last_input or self._last_input != input:
                self._client.say(input)
            self._last_input = input


    def _render_lobby_state(self):
        self._window.fill(ClientConstants.BACKGROUND_COLOR)
        ready_count = len([x for x in self._game_state.player_list if x.player_status == PlayerStatus.PlayerStatus.READY])
        player_count = len(self._game_state.player_list)

        font = pg.font.Font(None, 32)

        # storing all elements for easy rendering later
        render_elements = []

        text = font.render(f'Lobby ID: {self._game_state.game_server_id}', True, ClientConstants.WHITE)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, 150)
        render_elements.append((text, text_rect))

        text = font.render('Waiting For Start', True, GREEN)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT // 2 - 100)
        render_elements.append((text, text_rect))

        text = font.render(f'{ready_count} of {player_count} Players ready', True, ClientConstants.BLUE)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT // 2)
        render_elements.append((text, text_rect))

        ready_state = False
        color = None    # None => Spectator

        # check whether client is ready
        for player in self._game_state.player_list:
            if player.id == self._player_id:
                if player.player_status == PlayerStatus.PlayerStatus.READY:
                    ready_state = True
                if player.color is None:
                    color_text = font.render("You are a Spectator", True, (0, 0, 0))
                else:
                    color_text = font.render("You are a Player", True, player.color)

        color_rect = color_text.get_rect()
        color_rect.center = (WIDTH // 2, HEIGHT // 2 + 100)
        render_elements.append((color_text, color_rect))


        if ready_state:
            text = font.render('Ready', True, GREEN)
        else:
            text = font.render('Not Ready', True, (255, 0, 0))

        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT - 100)
        render_elements.append((text, text_rect))

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                input = PlayerInput.PlayerInput()
                if event.key == pg.K_SPACE:
                    input.space = True
                elif event.key == pg.K_LEFT:
                    input.left = True
                elif event.key == pg.K_RIGHT:
                    input.right = True
                self._client.say(input)

        # rendering elements
        for element in render_elements:
            self._window.blit(element[0], element[1])

    def _render_menu(self):
        font = pg.font.Font(None, 32)
        color_inactive = pg.Color('lightskyblue3')
        color_active = pg.Color('dodgerblue2')

        input_box = pg.Rect(WIDTH // 2 + 100, HEIGHT // 2 + 34, 140, 32)
        button_text = font.render("New Lobby", True, ClientConstants.WHITE)
        button_rect = pg.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 34, 120, 32)
        button_rect.center = (WIDTH // 2 - 100, HEIGHT // 2 + 50)

        button_rect.width += 5
        button_rect.width += 5

        button_color = color_inactive

        field_color = color_inactive
        active = False
        text = ''
        done = False


        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    done = True
                if event.type == pg.MOUSEMOTION:
                    if button_rect.collidepoint(event.pos):
                        button_color = color_active
                    else:
                        button_color = color_inactive
                if event.type == pg.MOUSEBUTTONDOWN:
                    # If the user clicked on the input_box rect.
                    if input_box.collidepoint(event.pos):
                        # Toggle the active variable.
                        active = not active
                    else:
                        active = False
                    if button_rect.collidepoint(event.pos):
                        self.join(-1)
                        return
                    # Change the current color of the input box.
                    field_color = color_active if active else color_inactive
                if event.type == pg.KEYDOWN:
                    if active:
                        if event.key == pg.K_RETURN:
                            self.join(int(text))
                            return
                        elif event.key == pg.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            self._window.fill(ClientConstants.BACKGROUND_COLOR)
            # Render the current text.
            txt_surface = font.render(text, True, field_color)
            # Resize the box if the text is too long.
            width = max(60, txt_surface.get_width()+10)
            input_box.w = width
            # Blit the text.
            self._window.blit(txt_surface, (input_box.x+5, input_box.y+5))
            self._window.blit(button_text, (button_rect.x + 5, button_rect.y + 5))
            # Blit the input_box rect.
            pg.draw.rect(self._window, field_color, input_box, 2)
            pg.draw.rect(self._window, button_color, button_rect, 2)
            pg.display.flip()

    def _handle_game_state(self, game_state: GameState):
        self._game_state = game_state
        print(game_state.state)
        self._force_wait = False

        # detecting own player_id (assigned by server)
        if self._player_id is None:
            self._player_id = self._game_state.player_list[-1].id

    def start(self):
        self.init_client(name="test_user")
        clock = pg.time.Clock()
        pg.init()
        while True:
            if not self._game_state and not self._force_wait:
                self._render_menu()
            elif not self._force_wait:
                if self._game_state.state == LobbyState.LOBBY:
                    self._render_lobby_state()
                elif self._game_state.state == LobbyState.IN_GAME:
                    self._render_game()
                elif self._game_state.state == LobbyState.BETWEEN_GAMES:
                    self._render_between_rounds()
            clock.tick(60)
            pg.display.update()
        pg.quit()


if __name__ == '__main__':
    gameClient = GameClient()
    gameClient.start()
