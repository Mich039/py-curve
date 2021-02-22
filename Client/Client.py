from enum import Enum
import pygame as pg
from GameObjects.Input import PlayerInput, PlayerLobbyInput
from GameObjects import GameState, PlayerStatus
from GameObjects.LobbyState import LobbyState
from Socket.client import Client

IP = "127.0.0.1"
PORT = 4321
WIDTH = 1000
HEIGHT = 1000
BASE_SPEED = 1.0

pg.display.set_caption("Client")


class GameClient:

    def __init__(self):
        self._gameState: GameState = None
        self._client: Client = None
        self._window = pg.display.set_mode((WIDTH, HEIGHT))

    def init_client(self, ip=IP, port=PORT, name="User"):
        self._client = Client(ip, port, name)
        self._client.receive_message_event = self.handle_gamestate

    def join(self, id: int):
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

    def PointsToTuple(self, points):
        res = []
        for p in points:
            res.append((p.x, p.y))
        return res

    def render_between_rounds(self):
        text_recs = []
        texts = []
        font = pg.font.Font(None, 32)

        self._window.fill((50, 50, 50))

        h = font.render("--- Score ---")
        hr = h.get_rect()
        self._window.blit(h, hr)

        count = 0
        for player in self._gameState.player_list:
            count = count + 1
            color = player.color
            t = font.render(f'{player.score.score_points}', True, color)
            tr = t.get_rect()
            tr.center = (WIDTH // 2, HEIGHT // 2 + 10 * count)
            text_recs.append(tr)
            texts.append(t)
        for i in range(len(texts)):
            self._window.blit(texts[i], text_recs[i])

    def render_game(self):
        self._window.fill((50, 50, 50))
        for player in self._gameState.player_list:
            for sublist in player.body:
                if len(sublist) < 2:
                    continue
                sublist = self.PointsToTuple(sublist)
                    # for p in self.points:
                    #    pygame.draw.circle(win, self.color, p, 3, 0)
                pg.draw.lines(self._window, (0, 255, 0), points=sublist, closed=False, width=2)
                pg.draw.lines(self._window, (0, 255, 0), points=sublist, closed=False, width=-2)
            pg.draw.circle(self._window, (255, 255, 0), (player.head.x, player.head.y), 4)


        input = PlayerInput.PlayerInput()
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        input.left = True
                    elif event.key == pg.K_RIGHT:
                        input.right = True
            self._client.say(input)



    def render_lobby_state(self):
        self._window.fill((30, 30, 30))
        readyCount = len([x for x in self._gameState.player_list if x.player_status == PlayerStatus.PlayerStatus.READY])
        playerCount = len(self._gameState.player_list)

        blue = (0, 0, 128)
        green = (0, 255, 0)

        font = pg.font.Font(None, 32)
        text = font.render('Waiting For Start', True, green, blue)
        textRect = text.get_rect()
        textRect.center = (WIDTH // 2, HEIGHT // 2 - 100)

        for event in pg.event.get():
            # toggle ready
            if event.type == pg.KEYDOWN:
                input = PlayerInput.PlayerInput()
                if event.key == pg.K_SPACE:
                    print("SPACE pressed")
                    #ready = not ready
                    input.space = True
                    #print("SPACE")
                elif event.key == pg.key.K_LEFT:
                    input.left = True
                elif event.key == pg.key.K_RIGHT:
                    input.right = True
                self._client.say(input)

        readyText = font.render(f'{readyCount} of {playerCount} Players ready', True, green)
        readyRect = readyText.get_rect()
        readyRect.center = (WIDTH // 2, HEIGHT // 2 + 100)
        self._window.blit(text, textRect)
        self._window.blit(readyText, readyRect)


    def render_menu(self):
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
                            self.join((int)(text))
                            return
                            text = ''
                        elif event.key == pg.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            self._window.fill((30, 30, 30))
            # Render the current text.
            txt_surface = font.render(text, True, color)
            # Resize the box if the text is too long.
            width = max(60, txt_surface.get_width()+10)
            input_box.w = width
            # Blit the text.
            self._window.blit(txt_surface, (input_box.x+5, input_box.y+5))
            # Blit the input_box rect.
            pg.draw.rect(self._window, color, input_box, 2)
            pg.display.flip()

    def handle_gamestate(self, gameState):
        self._gameState = gameState
        print(gameState.state)

    def start(self):
        self.init_client(name="test_user")
        clock = pg.time.Clock()
        pg.init()
        while True:
            #print("while true")
            if not self._gameState:
                self.render_menu()
            else:
                if self._gameState.state == LobbyState.LOBBY:
                    #print("hola")
                    self.render_lobby_state()
                elif self._gameState.state == LobbyState.IN_GAME:
                    self.render_game()
                elif self._gameState.state == LobbyState.BETWEEN_GAMES:
                    self.render_game(True)
            clock.tick(100)
            pg.display.update()
        pg.quit()

if __name__ == '__main__':
    gameClient = GameClient()
    gameClient.start()
