import sched
import time
import random
from typing import Dict, Tuple, Optional
import logging

from GameObjects.PowerUp import PowerUp
from GameObjects.PowerUpType import PowerUpType
from GameObjects.Color import Color
from GameObjects.LobbyState import LobbyState
from GameObjects.Player import Player
from GameObjects.Input.PlayerInput import PlayerInput
from GameObjects.PlayerStatus import PlayerStatus
from GameObjects.Point import Point
from GameServer import PowerUpHelper
from GameServer.GameServerWrappers.GameStateWrapper import GameStateWrapper
from GameServer.GameServerWrappers.PlayerInputWrapper import PlayerInputWrapper
from GameServer.GameServerWrappers.PlayerWrapper import PlayerWrapper
import GameServer.ServerConstants as ServerConstants


class GameServer:
    # Add, input, remove
    def __init__(self, id: int):
        self._log = logging.getLogger('GameServer {0}'.format(id))
        self._id = id
        self._new_server: bool = True
        self._gameState: GameStateWrapper = GameStateWrapper(id)
        self._broadcast = None
        self._remove_game_server = None
        self._inputs: Dict[str, PlayerInputWrapper] = dict()
        self._scheduler: sched.scheduler = sched.scheduler(time.time, time.sleep)
        self._canceled: bool = False
        self._player_colors = {ServerConstants.PLAYER_COLORS[k]: None for k in range(len(ServerConstants.PLAYER_COLORS))}
        self._log.info("Created")

    def start(self):
        """
        Start a schedule to loop in a interval through the server logic.
        :return:
        """
        self._log.info("Server with id {id} has started".format(id=self.id))
        self._gameState.state = LobbyState.LOBBY
        self._scheduler.enter(delay=0, priority=0, action=self._tick)
        self._scheduler.run(blocking=True)
        if self._remove_game_server is not None:
            self._remove_game_server(self)

    @property
    def remove_game_server(self):
        return self._remove_game_server

    @remove_game_server.setter
    def remove_game_server(self, value):
        self._remove_game_server = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def broadcast(self):
        return self._broadcast

    @broadcast.setter
    def broadcast(self, value):
        self._broadcast = value

    def add_player(self, id: str, username: str):
        """
        Add a new player to the GameServer by id and username.
        Broadcast the changes (Lobby) to all players.
        :param id: Player id
        :param username: Player username
        :return:
        """
        self._log.info("Add player with id {0}".format(id))
        new_payer = PlayerWrapper(Player(id, username))
        new_payer.player.player_status = self._get_current_default_player_status()
        new_payer.player.color = self._get_player_color(id)
        self._gameState.player_list[id] = new_payer
        self._new_server = False
        self._broadcast_state()

    def receive_player_input(self, id: str, player_input: PlayerInput):
        """
        Receive player input and save it under player id.
        Player input has to be newer than the current one.
        :param id: Player id
        :param player_input: Player input
        :return:
        """
        if id not in self._inputs or self._inputs[id].timestamp < player_input.timestamp:
            self._inputs[id] = PlayerInputWrapper(player_input)
        else:
            print("Player with id: {id} sent outdated Input".format(id=id))

    def remove_player(self, id: str):
        """
        Remove a player by id.
        The player will be removed on the next tick.
        :param id: Player id.
        :return:
        """
        self._gameState.remove(id)

    def _get_current_default_player_status(self) -> PlayerStatus:
        """
        Get the current PlayerStatus for the GameServer.
        :return: PlayerStatus
        """
        if self._gameState.state == LobbyState.IN_GAME:
            return PlayerStatus.SPECTATING
        else:
            return PlayerStatus.NOT_READY

    def _get_player_color(self, player_id: str):
        """
        Get the color of the player by id.
        :param player_id:
        :return:
        """
        for k, v in self._player_colors.items():
            print(k, v)
            if v is None:
                print("free color found")
                self._player_colors[k] = player_id
                print("returning color")
                return k

    def _remove_players(self) -> bool:
        """
        Removes all players contained in the to_remove list and returns if at least one player has been removed
        :return:
        """
        change: bool = False
        for player_id in self._gameState.to_remove:
            change = self._gameState.player_list.pop(player_id, None) is not None or change
            self._inputs.pop(player_id, None)
            self._log.info("Removed Player '{id}' from game state".format(id=player_id))
            self._gameState.to_remove.clear()
        return change

    def _init_between_games(self):
        """
        Set PlayerStatus to Not_Ready on all players.
        :return:
        """
        self._gameState.state = LobbyState.BETWEEN_GAMES
        for player in [player for player in self._gameState.player_list.values() if
                       not player.player.player_status == PlayerStatus.SPECTATING]:
            player.player.player_status = PlayerStatus.NOT_READY

    def _init_new_round(self):
        """
        Initialise new round.
        Set PlayerStatus to ALIVE and reset the body of all players.
        Also set the position of each player for the next round.
        :return:
        """
        # Remove all the power ups
        self._gameState.ground_power_up.clear()
        for player in [player for player in self._gameState.player_list.values() if
                       not player.player.player_status == PlayerStatus.SPECTATING]:
            player.player.player_status = PlayerStatus.ALIVE
            player.player.active_power_ups.clear()
            player.clear_body()
            player.init_position(GameServer._get_random_point(), GameServer._get_random_angle())

    def _init_new_game(self):
        """
        Initialise new game and reset score.
        :return:
        """
        for player in self._gameState.player_list.values():
            player.reset_score()
        self._init_new_round()

    def _broadcast_state(self):
        """
        Tell the Socket server to broadcast the GameState to all players of this GameServer.
        :return:
        """
        if self._broadcast is not None:
            self._broadcast(self.id, self._gameState.to_game_state())

    def _tick(self):
        """
        This Method is called everytime the scheduler calls.
        If the lobby is still active (Has players) it will refresh the scheduler tick and call the current tick function
        according to the game state. Additionally it also sets the inputs to processed.
        :return:
        """
        # Check if there are any players in that Lobby
        self._canceled = len(self._gameState.player_list) == 0

        if not self._canceled or self._new_server:
            start_time = time.time()
            next_start_time = start_time + 1 / ServerConstants.TICK_RATE
            time_available = next_start_time*1000 - start_time*1000
            self._scheduler.enterabs(time=next_start_time, priority=0, action=self._tick)

        # React depending on State
        if self._gameState.state == LobbyState.IN_GAME:
            self._in_game_tick()
            #  time_taken = (time.time() * 1000 - start_time * 1000)
            #  print("Time taken: {time:.10f} ms {time_perc}%".format(time=time_taken, time_perc=time_taken / time_available))
        elif self._gameState.state == LobbyState.BETWEEN_GAMES:
            self._between_game_tick()
        else:
            self._lobby_tick()

        self._inputs_processed()

    @staticmethod
    def _get_random_angle() -> float:
        """
        Get a random angle.
        :return:
        """
        return random.uniform(0, 360)

    @staticmethod
    def _get_random_point() -> Point:
        """
        Get a random point in the arena.
        :return:
        """
        return Point(random.uniform(0, ServerConstants.PLAY_AREA_SIZE),
                     random.uniform(0, ServerConstants.PLAY_AREA_SIZE))

    def _inputs_processed(self):
        """
        Set all player inputs to processed.
        :return:
        """
        for input in self._inputs.values():
            input.processed = True

    def _lobby_tick(self):
        change: bool = False
        handle_result = self._handle_ready_inputs()
        change = handle_result[0]

        change = change or self._handle_color_inputs()

        change = change or self._remove_players()

        if handle_result[1]:
            self._init_new_game()
            self._gameState.state = LobbyState.IN_GAME

        elif change:
            self._broadcast_state()

    def _players_alive(self) -> bool:
        """ Checks if more than one player is alive. True if so False if not """
        return len([player for player in self._gameState.player_list.values() if
                    player.player.player_status == PlayerStatus.ALIVE]) > 1

    def _next_player_color(self, player_id: str, reverse=False):
        """
        Changes the color of the player specified by the player id to the next available color or Spectator.
        The reverse Flag specifies the direction to loop.
        """
        # Get the current color of the player in question
        old_color: Optional[Color] = self._gameState.player_list[player_id].player.color
        # Reset the player color dictionary so that the index matches in the available_color_list
        if old_color is not None:
            self._player_colors[old_color] = None

        # Create a list that also contains None (Spectator)
        available_color_list = [None, *(color for color, player in self._player_colors.items() if player is None)]

        # Get the index of the current color
        if old_color is not None:
            color_index = available_color_list.index(old_color)
        else:
            # None is the always on index 0
            color_index = 0

        # Look at the next available neighbor. This loops that no error can occur
        offset = 1 if not reverse else -1
        new_color = available_color_list[(color_index + offset) % len(available_color_list)]

        # When the player has an actual color set it in the player color dict so the color is occupied
        if new_color is not None:
            self._player_colors[new_color] = player_id
            self._gameState.player_list[player_id].player.player_status = PlayerStatus.NOT_READY
        else:
            self._gameState.player_list[player_id].player.player_status = PlayerStatus.SPECTATING

        # Set the color in the player to send to the client
        self._gameState.player_list[player_id].player.color = new_color

    def _calculate_score(self):
        for player_id, player in self._gameState.player_list.items():
            if player.player.player_status == PlayerStatus.ALIVE:
                player.player.score.score_points += ServerConstants.DEATH_SCORE

    def _in_game_tick(self):
        #  move_start_time = time.time() * 1000
        self._spawn_power_ups()
        for player_id, player in self._gameState.player_list.items():
            if player.player.player_status == PlayerStatus.ALIVE:
                player.power_up_tick()
                if not player.move(self._inputs[player_id], game_state=self._gameState):
                    player.player.player_status = PlayerStatus.DEAD
                    player.player.score.deaths += 1
                    self._calculate_score()
                    if not self._players_alive():
                        self._init_between_games()
        #  print("Move took {t} ms".format(t=(time.time()*1000)-move_start_time))
        self._broadcast_state()

    def _spawn_power_ups(self):
        if random.uniform(0, 100) <= ServerConstants.POWER_UP_CHANCE:
            # Pick one of the PowerUps
            type: PowerUpType = random.choice(list(PowerUpType))
            # Setup the new PowerUp
            new_power_up = PowerUpHelper.create_power_up(type, self._get_random_point())
            # Add to game state
            self._gameState.ground_power_up.append(new_power_up)

    def _handle_ready_inputs(self) -> Tuple[bool, bool]:
        """
        Handles the Ready Inputs for the States Lobby and Between Games.

        :returns
        A Tuple with two entries: The first one represents if a change happened.
        The second element is true if all players are ready
        """
        # Process Inputs
        change: bool = False
        for key, value in [item for item in self._inputs.items() if not self._gameState.player_list[item[0]].player.player_status == PlayerStatus.SPECTATING]:
            if value.space and not value.processed:
                old_state = self._gameState.player_list[key].player.player_status
                self._gameState.player_list[key].player.player_status = \
                    PlayerStatus.READY if old_state == PlayerStatus.NOT_READY else PlayerStatus.NOT_READY
                change = True

        # Check if all non spectating Players are ready
        all_ready: bool = len([player for player in self._gameState.player_list.values() if not player.player.player_status == PlayerStatus.SPECTATING]) > 0
        for player_id, player in self._gameState.player_list.items():
            all_ready = all_ready and not player.player.player_status == PlayerStatus.NOT_READY
        return change, all_ready

    def _handle_color_inputs(self) -> bool:
        """
        Handles the LEFT and RIGHT inputs of players in the lobby.
        These Inputs will change the player color or set the player as a spectator
        :return:
        If a change occurred this method returns true, else false
        """
        change: bool = False
        for key, value in [item for item in self._inputs.items() if not item[1].processed]:
            if value.right:
                self._next_player_color(key)
                change = True
            if value.left:
                self._next_player_color(key, reverse=True)
                change = True

        return change

    def _between_game_tick(self):
        """
        Choose a action between games.
        If all player are ready, set the GameSate to IN_GAME and initialise a new game.
        If a player has to be removed or a change occurred, broadcast them to all players.
        :return:
        """
        handle_result = self._handle_ready_inputs()

        if handle_result[1]:
            self._init_new_round()
            self._gameState.state = LobbyState.IN_GAME

        elif handle_result[0] or self._remove_players():
            self._broadcast_state()
