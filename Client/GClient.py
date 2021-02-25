from enum import Enum
import pygame as pg

from Client import ClientConstants
from GameObjects.Input import PlayerInput, PlayerLobbyInput
from GameObjects import GameState, PlayerStatus
from GameObjects.LobbyState import LobbyState
from Socket.client import Client

IP = "gattinger.ddns.net"
PORT = 4321
WIDTH = 1000
HEIGHT = 1000

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

    def join(self, id: int, username: str):
        if not username or len(username) < 1:
            return False

        self.init_client(name=username)

        self._force_wait = True
        lobby = PlayerLobbyInput.PlayerLobbyInput()
        lobby.username = self._client.name
        if id < 0:
            lobby.create_new_lobby = True
        else:
            lobby.create_new_lobby = False
            lobby.lobby_id = id
        self._client.say(lobby)
        return True

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

        h = font.render("--- Score ---", True, ClientConstants.RED)
        hr = h.get_rect()
        hr.center = (WIDTH // 2, 100)
        self._window.blit(h, hr)

        count = 0
        ready_state = False
        for player in self._game_state.player_list:
            if player.player_status is not PlayerStatus.PlayerStatus.SPECTATING:
                count = count + 1
                color = player.color
                if player.id == self._player_id:
                    if player.player_status == PlayerStatus.PlayerStatus.READY:
                        ready_state = True
                    font.set_italic(True)
                else:
                    font.set_italic(False)
                ready_text = "Ready" if player.player_status == PlayerStatus.PlayerStatus.READY else "Not Ready"
                t = font.render(f'{player.name}: {player.score.score_points} ({ready_text})', True, color)
                tr = t.get_rect()
                tr.center = (WIDTH // 2, 200 + 30 * count)
                text_recs.append(tr)
                texts.append(t)

        font.set_italic(False)
        if ready_state:
            t = font.render('Ready', True, ClientConstants.GREEN)
        else:
            t = font.render('Not Ready', True, ClientConstants.RED)
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
            if player.player_status is not PlayerStatus.PlayerStatus.SPECTATING:
                for sublist in player.body:
                    if len(sublist) < 2:
                        continue
                    sublist = _points_to_tuples(sublist)
                    pg.draw.lines(self._window, player.color, points=sublist, closed=False, width=5)
                pg.draw.circle(self._window, (255, 255, 0), (player.head.x, player.head.y), 2.5)

        for power_up in self._game_state.ground_power_up:
            pg.draw.circle(self._window, ClientConstants.POWER_UP_COLORS[power_up.power_up_type], (power_up.location.x, power_up.location.y), ClientConstants.POWER_UP_RADIUS)


        for event in pg.event.get():
            player_input = PlayerInput.PlayerInput()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    player_input.left = True
                elif event.key == pg.K_RIGHT:
                    player_input.right = True
            if not self._last_input or self._last_input != player_input:
                self._client.say(player_input)
            self._last_input = player_input


    def _render_lobby_state(self):
        self._window.fill(ClientConstants.BACKGROUND_COLOR)
        #ready_count = len([x for x in self._game_state.player_list if x.player_status == PlayerStatus.PlayerStatus.READY])
        #player_count = len(self._game_state.player_list)

        font = pg.font.Font(None, 32)

        # storing all elements for easy rendering later
        render_elements = []


        text = font.render(f'Lobby ID: {self._game_state.game_server_id}', True, ClientConstants.WHITE)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, 150)
        render_elements.append((text, text_rect))

        text = font.render('Waiting For Start', True, ClientConstants.GREEN)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT // 2 - 100)
        render_elements.append((text, text_rect))

        #text = font.render(f'{ready_count} of {player_count} Players ready', True, ClientConstants.BLUE)
        #text_rect = text.get_rect()
        #text_rect.center = (WIDTH // 2, HEIGHT // 2)
        #render_elements.append((text, text_rect))

        own_player_state = None
        color = None    # None => Spectator

        # check whether client is ready
        count = 0
        for player in self._game_state.player_list:
            count += 1
            if player.id == self._player_id:
                own_player_state = player.player_status
                if player.color is None:
                    text = font.render("You are a Spectator", True, ClientConstants.BLACK)
                else:
                    text = font.render("You are a Player", True, player.color)
            else:
                ready_text = ''
                if player.player_status == PlayerStatus.PlayerStatus.SPECTATING:
                    ready_text = 'Spectating'
                elif player.player_status == PlayerStatus.PlayerStatus.READY:
                    ready_text = 'Ready'
                else:
                    ready_text = 'Not Ready'
                color = player.color if player.color is not None else ClientConstants.BLACK
                text = font.render(f'{player.name} ({ready_text})', True, color)
                #text_rect = text.get_rect()
                #text_rect.center = (WIDTH // 2, HEIGHT // 2 + 50 * count)
                #render_elements.append((text, text_rect))

            text_rect = text.get_rect()
            text_rect.center = (WIDTH // 2, HEIGHT // 2 + 50 * count)
            render_elements.append((text, text_rect))

        if own_player_state == PlayerStatus.PlayerStatus.READY:
            text = font.render('Ready', True, ClientConstants.GREEN)
        elif own_player_state == PlayerStatus.PlayerStatus.NOT_READY:
            text = font.render('Not Ready', True, ClientConstants.RED)
        elif own_player_state == PlayerStatus.PlayerStatus.SPECTATING:
            text = font.render('Spectating', True, ClientConstants.WHITE)

        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT - 100)
        render_elements.append((text, text_rect))

        for event in pg.event.get():
            player_input = PlayerInput.PlayerInput()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    player_input.space = True
                elif event.key == pg.K_LEFT:
                    player_input.left = True
                elif event.key == pg.K_RIGHT:
                    player_input.right = True
            if not self._last_input or self._last_input != player_input:
                self._client.say(player_input)
            self._last_input = player_input

        # rendering elements
        for element in render_elements:
            self._window.blit(element[0], element[1])

    def _render_menu(self):
        font = pg.font.Font(None, 32)
        color_inactive = pg.Color('lightskyblue3')
        color_active = pg.Color('dodgerblue2')

        lobby_box = pg.Rect(WIDTH // 2 + 100, HEIGHT // 2 + 34, 140, 32)
        username_box = pg.Rect(WIDTH // 2, HEIGHT // 2 + 134, 140, 32)
        username_header = font.render("Enter Username:", True, ClientConstants.WHITE)
        username_header_box = username_header.get_rect()
        username_header_box.center = (WIDTH // 2 - 100, HEIGHT // 2 + 150)

        button_text = font.render("New Lobby", True, ClientConstants.WHITE)
        button_rect = pg.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 34, 120, 32)
        button_rect.center = (WIDTH // 2 - 100, HEIGHT // 2 + 50)

        button_rect.width += 5
        button_rect.width += 5

        button_color = color_inactive

        lobby_field_color = color_inactive
        username_field_color = color_inactive

        lobby_field_active = False
        username_field_active = False

        lobby_id = ''
        username = ''

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.MOUSEMOTION:
                    if button_rect.collidepoint(event.pos):
                        button_color = color_active
                    else:
                        button_color = color_inactive
                if event.type == pg.MOUSEBUTTONDOWN:
                    # If the user clicked on the input_box rect.
                    if lobby_box.collidepoint(event.pos):
                        # Toggle the active variable.
                        lobby_field_active = True
                        lobby_field_color = color_active
                        username_field_active = False
                        username_field_color = color_inactive
                    elif username_box.collidepoint(event.pos):
                        lobby_field_active = False
                        lobby_field_color = color_inactive
                        username_field_active = True
                        username_field_color = color_active
                    else:
                        lobby_field_active = False
                        username_field_active = False
                        lobby_field_color = color_inactive
                        username_field_color = color_inactive
                    if button_rect.collidepoint(event.pos):
                        if self.join(-1, username):
                            return
                        else:
                            username_field_color = ClientConstants.RED

                    # Change the current color of the input box.
                    # lobby_field_color = color_active if lobby_field_active else color_inactive
                    # username_field_color = color_active if username_field_active else color_inactive

                if event.type == pg.KEYDOWN:
                    if lobby_field_active:
                        if event.key == pg.K_RETURN:
                            if self.join(int(lobby_id), username):
                                return
                            else:
                                username_field_color = ClientConstants.RED
                        elif event.key == pg.K_BACKSPACE:
                            lobby_id = lobby_id[:-1]
                        else:
                            lobby_id += event.unicode
                    elif username_field_active:
                        if event.key == pg.K_BACKSPACE:
                            username = username[:-1]
                        else:
                            username += event.unicode

            self._window.fill(ClientConstants.BACKGROUND_COLOR)
            # Render the current text.
            lobby_surface = font.render(lobby_id, True, lobby_field_color)
            username_surface = font.render(username, True, username_field_color)

            # Resize the box if the text is too long.
            width = max(60, lobby_surface.get_width()+10)
            lobby_box.w = width
            # Blit the text.
            self._window.blit(lobby_surface, (lobby_box.x+5, lobby_box.y+5))
            self._window.blit(username_surface, (username_box.x+5, username_box.y+5))
            self._window.blit(button_text, (button_rect.x + 5, button_rect.y + 5))
            self._window.blit(username_header, username_header_box)
            # Blit the input_box rect.
            pg.draw.rect(self._window, lobby_field_color, lobby_box, 2)
            pg.draw.rect(self._window, username_field_color, username_box, 2)
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
