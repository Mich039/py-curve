from enum import Enum
import pygame as pg

from Client import ClientConstants
from GameObjects.Input import PlayerInput, PlayerLobbyInput
from GameObjects import GameState, PlayerStatus
from GameObjects.LobbyState import LobbyState
from GameObjects.PowerUpType import PowerUpType
from Socket.client import Client

WIDTH = 1000
HEIGHT = 1000
pg.display.set_caption("CurveFever Client")


def points_to_tuples(points):
    # Points arent compatible with PyGame and need to be converted to tuples
    res = []
    for p in points:
        res.append((p.x, p.y))
    return res


class GameClient:
    def __init__(self):
        self._game_state: GameState = None
        self._client: Client = None
        self._window = pg.display.set_mode((WIDTH, HEIGHT))
        self._force_wait = False
        self._last_input = None

    def _init_client(self, ip=ClientConstants.IP, port=ClientConstants.PORT, name="User"):
        self._client = Client(ip, port, name)
        self._client.receive_message_event = self._handle_game_state

    def _join(self, id: int, username: str):
        if not username or len(username) < 1:
            return False

        self._init_client(name=username)

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

    def _render_between_rounds(self):
        """
        Instructs PyGame to draw the pause/score-screen
        Should be called periodically during the main loop if lobby_state (part of game_state) is set to between_game.
        """

        # storing elements to render in a list
        # containing tuples will be rendered every iteration
        render_elements = []
        font = pg.font.Font(None, 32)

        self._window.fill(ClientConstants.BACKGROUND_COLOR)

        text = font.render("--- Score ---", True, ClientConstants.RED)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, 100)
        render_elements.append((text, text_rect))

        count = 0
        ready_state = None
        for player in self._game_state.player_list:
            if player.id == self._client.client_id:
                ready_state = player.player_status
                font.set_italic(True)
            else:
                font.set_italic(False)
            if player.player_status is not PlayerStatus.PlayerStatus.SPECTATING:
                count = count + 1
                color = player.color
                ready_text = "Ready" if player.player_status == PlayerStatus.PlayerStatus.READY else "Not Ready"
                text = font.render(f'{player.name}: {player.score.score_points} ({ready_text})', True, color)
                text_rect = text.get_rect()
                text_rect.center = (WIDTH // 2, 200 + 30 * count)
                render_elements.append((text, text_rect))

        font.set_italic(False)
        if ready_state == PlayerStatus.PlayerStatus.READY:
            text = font.render('Ready', True, ClientConstants.GREEN)
        elif ready_state == PlayerStatus.PlayerStatus.NOT_READY:
            text = font.render('Not Ready', True, ClientConstants.RED)
        else:
            text = font.render('Spectating', True, ClientConstants.WHITE)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT - 50)
        render_elements.append((text, text_rect))

        for e in render_elements:
            self._window.blit(e[0], e[1])

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                player_input = PlayerInput.PlayerInput()
                if event.key == pg.K_SPACE:
                    player_input.space = True
                self._client.say(player_input)

    def _render_game(self):
        """
        Instructs PyGame to draw the current game_state.
        Should be called periodically during the main loop if lobby_state (part of game_state) is set to in-game.
        """
        self._window.fill(ClientConstants.BACKGROUND_COLOR)
        for player in self._game_state.player_list:
            if player.player_status is not PlayerStatus.PlayerStatus.SPECTATING:
                for sublist in player.body:
                    if len(sublist) < 2:
                        continue
                    sublist = points_to_tuples(sublist)
                    pg.draw.lines(self._window, player.color, points=sublist, closed=False, width=ClientConstants.LINE_THICKNESS)

                head_color = ClientConstants.YELLOW
                draw_square = False
                for power_up in player.active_power_ups:
                    if power_up.power_up_type == PowerUpType.ENEMY_INVERSE:
                        head_color = ClientConstants.BLUE
                    elif power_up.power_up_type == PowerUpType.CORNER or power_up.power_up_type == PowerUpType.ENEMY_CORNER:
                        draw_square = True
                if draw_square:
                    rect = pg.Rect(0, 0, 5, 5)
                    rect.center = (player.head.x, player.head.y)
                    pg.draw.rect(self._window, head_color, rect)
                else:
                    pg.draw.circle(self._window, head_color, (player.head.x, player.head.y), ClientConstants.LINE_THICKNESS / 2)

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
        """
        Instructs PyGame to draw the lobby_screen.
        Should be called periodically during the main loop if lobby_state (part of game_state) is set to lobby.
        """

        # storing elements to render in a list
        # containing tuples will be rendered every iteration
        render_elements = []

        self._window.fill(ClientConstants.BACKGROUND_COLOR)
        font = pg.font.Font(None, 32)

        # lobby label
        text = font.render(f'Lobby ID: {self._game_state.game_server_id}', True, ClientConstants.WHITE)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, 150)
        render_elements.append((text, text_rect))

        # waiting for start label
        text = font.render('Waiting For Start', True, ClientConstants.GREEN)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT // 2 - 100)
        render_elements.append((text, text_rect))

        # will be stored for rendering the own player status
        # after the player list was rendered
        own_player_state = None

        count = 0
        for player in self._game_state.player_list:
            # rendering players and their states
            count += 1  # for vertical offset calculation
            if player.id == self._client.client_id:
                own_player_state = player.player_status
                if player.color is None:
                    text = font.render("You are a Spectator", True, ClientConstants.BLACK)
                else:
                    text = font.render("You are a Player", True, player.color)
            else:
                if player.player_status == PlayerStatus.PlayerStatus.SPECTATING:
                    ready_text = 'Spectating'
                elif player.player_status == PlayerStatus.PlayerStatus.READY:
                    ready_text = 'Ready'
                else:
                    ready_text = 'Not Ready'
                color = player.color if player.color is not None else ClientConstants.BLACK
                text = font.render(f'{player.name} ({ready_text})', True, color)

            text_rect = text.get_rect()
            text_rect.center = (WIDTH // 2, HEIGHT // 2 + 50 * count)
            render_elements.append((text, text_rect))

        # rendering own player_state
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
            # avoid spamming the same input over and over again
            if not self._last_input or self._last_input != player_input:
                self._client.say(player_input)
            self._last_input = player_input

        # rendering elements
        for element in render_elements:
            self._window.blit(element[0], element[1])

    def _render_menu(self):
        # storing elements to render in a list
        # containing tuples will be rendered every iteration
        render_elements = []

        # used fonts
        header_font = pg.font.Font(None, 48)
        font = pg.font.Font(None, 32)

        # colors indicating the selection state of the input fields
        color_inactive = ClientConstants.FIELD_INACTIVE_COLOR
        color_active = ClientConstants.FIELD_ACTIVE_COLOR

        # initializing input fields
        lobby_field_color = color_inactive
        username_field_color = color_inactive
        lobby_field_active = False
        username_field_active = False
        lobby_id = ''
        username = ''

        # defining input boxes for lobby_id and username
        lobby_box = pg.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 50, 140, 32)
        lobby_box.bottomleft = (WIDTH // 2 + 50, HEIGHT // 2 + 100)
        username_box = pg.Rect(WIDTH // 2, HEIGHT // 2 - 116, 140, 32)
        username_box.bottomleft = (WIDTH // 2 + 50, HEIGHT // 2 - 95)

        # header
        text = header_font.render("CURVE FEVER 2.0", True, ClientConstants.GREEN)
        text_box = text.get_rect()
        text_box.center = (WIDTH // 2, HEIGHT // 2 - 300)
        render_elements.append((text, text_box))

        # username label
        text = font.render("Enter Username:", True, ClientConstants.WHITE)
        text_box = text.get_rect()
        text_box.bottomleft = (WIDTH // 2 - 200, HEIGHT // 2 - 100)
        render_elements.append((text, text_box))

        # lobby label
        text = font.render("Create or Join Lobby:", True, ClientConstants.WHITE)
        text_box = text.get_rect()
        text_box.bottomleft = (WIDTH // 2 - 200, HEIGHT // 2 + 50)
        render_elements.append((text, text_box))

        # new lobby button
        button_text = font.render("New Lobby", True, ClientConstants.FIELD_INACTIVE_COLOR)
        button_rect = pg.Rect(WIDTH // 2, HEIGHT // 2, 120, 32)
        button_rect.bottomleft = (WIDTH // 2 + 50, HEIGHT // 2 + 55)
        button_rect.width += 5
        button_rect.width += 5
        button_color = color_inactive

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.MOUSEMOTION:
                    # highlighting the button when hovering over it
                    if button_rect.collidepoint(event.pos):
                        button_color = color_active
                    else:
                        button_color = color_inactive
                if event.type == pg.MOUSEBUTTONDOWN:
                    # Toggle to active / inactive.
                    if lobby_box.collidepoint(event.pos):
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
                        # button press creates new lobby
                        # negative numbers indicate a new lobby should be created
                        if self._join(-1, username):
                            return
                        else:
                            # if len(username) < 1 join will return False
                            # a user/player-name is needed
                            username_field_color = ClientConstants.RED

                if event.type == pg.KEYDOWN:
                    # parsing input
                    if lobby_field_active:
                        if event.key == pg.K_RETURN:
                            if self._join(int(lobby_id), username):
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

            # resizes box if text is too long
            width = max(120, username_surface.get_width()+10)
            username_box.w = width
            width = max(60, lobby_surface.get_width()+10)
            lobby_box.w = width

            # render stored (constant) elements
            for e in render_elements:
                self._window.blit(e[0], e[1])

            # render input texts and rects
            self._window.blit(lobby_surface, (lobby_box.x+5, lobby_box.y+5))
            self._window.blit(username_surface, (username_box.x+5, username_box.y+5))
            self._window.blit(button_text, (button_rect.x + 5, button_rect.y + 5))
            pg.draw.rect(self._window, lobby_field_color, lobby_box, 2)
            pg.draw.rect(self._window, username_field_color, username_box, 2)
            pg.draw.rect(self._window, button_color, button_rect, 2)

            pg.display.flip()

    def _handle_game_state(self, game_state: GameState):
        """
        Should be registered on the receive_message_event of the client.
        Is used to update the game_state every time a new game state arrives.
        In case the force_wait flag was set to True, it will be reset to False again.
        :param game_state: current game_state broad-casted from the server
        """
        self._game_state = game_state
        self._force_wait = False

    def start(self):
        """
        Called once the game loop will start.
        This method will call other "render" methods based on the current LobbyState.
        """
        clock = pg.time.Clock()
        pg.init()
        while True:
            # force_wait is set if a crucial update was just sent to the server
            # and rendering without its respond would make no sense/lead to problems
            if not self._game_state and not self._force_wait:
                self._render_menu()
            elif not self._force_wait:
                if self._game_state.state == LobbyState.LOBBY:
                    self._render_lobby_state()
                elif self._game_state.state == LobbyState.IN_GAME:
                    self._render_game()
                elif self._game_state.state == LobbyState.BETWEEN_GAMES:
                    self._render_between_rounds()
            clock.tick(ClientConstants.FRAMES_PER_SECOND)
            pg.display.update()
        pg.quit()


if __name__ == '__main__':
    gameClient = GameClient()
    gameClient.start()
