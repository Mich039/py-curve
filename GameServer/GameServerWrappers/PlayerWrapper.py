import math

import GameObjects.Player as Player
from GameObjects.Point import Point
from GameServer.CollisionDetectionHelper import check_collision, is_relevant
from GameServer.GameServerWrappers.PlayerInputWrapper import PlayerInputWrapper
import GameServer.ServerConstants as ServerConstants


class PlayerWrapper:

    def __init__(self, player: Player):
        self._player: Player = player
        self._invisible_ticks: int = 0
        self._visible_ticks: int = 1000
        # self._is_alive: bool = False
        self._velocity: float = ServerConstants.BASE_SPEED

    @property
    def player(self) -> Player:
        return self._player

    @player.setter
    def player(self, value: Player):
        self._player = value

    @property
    def invisible_ticks(self) -> int:
        return self._invisible_ticks

    @invisible_ticks.setter
    def invisible_ticks(self, value: int):
        self._invisible_ticks = value

    @property
    def visible_ticks(self) -> int:
        return self._visible_ticks

    @visible_ticks.setter
    def visible_ticks(self, value: int):
        self._visible_ticks = value

    # @property
    # def is_alive(self) -> bool:
    #     return self._is_alive
    #
    # @is_alive.setter
    # def is_alive(self, value: bool):
    #     self._is_alive = value

    @property
    def velocity(self) -> float:
        return self._velocity

    @velocity.setter
    def velocity(self, value: float):
        self._velocity = value

    def reset_score(self):
        self._player.score.deaths = 0
        self._player.score.score_points = 0
        self._player.score.power_up_points = 0

    def init_position(self, pos: Point, angle: float):
        self._player.head = pos
        self._player.angle = angle
        # Remove Body
        self._player.body = [[], ]

    def rotate_by(self, deg):
        self.player.angle += math.radians(deg)

    def _check_player_collision(self, game_state) -> bool:
        # Loop over all segments in all other players
        for player in game_state.player_list.values():
            for segment in player.player.body:
                count = 0
                starting_point = None
                last_point = None
                for point in segment:
                    count = count + 1
                    if not is_relevant(self.player.head, point):
                        continue
                    if count % 2 == 0:
                        continue
                    if point == starting_point:
                        break
                    if starting_point is None:
                        starting_point = point
                        last_point = point
                    else:
                        if len(self.player.body[len(self.player.body) - 1]) > 0:
                            previous_point: Point = self.player.body[len(self.player.body) - 1][
                                len(self.player.body[len(self.player.body) - 1]) - 1]
                            if player.player.id == self.player.id:
                                # The previous point and the latest point in the body are the same.
                                # This should not cause a collision.
                                if previous_point == point:
                                    continue
                            if check_collision(self.player.head, previous_point, last_point, point):
                                return False
                    last_point = point
        return True

    def _check_for_wall_collision(self, game_state) -> bool:
        return not (self._player.head.x >= ServerConstants.PLAY_AREA_SIZE or self._player.head.x <= 0 or self._player.head.y >= ServerConstants.PLAY_AREA_SIZE or self._player.head.y <= 0)

    def move(self, input: PlayerInputWrapper, game_state) -> bool:
        if input.left:
            self.rotate_by(-ServerConstants.ROTATION_SPEED)

        if input.right:
            self.rotate_by(ServerConstants.ROTATION_SPEED)

        self.player.head.x += self.velocity * math.sin(self._player.angle)
        self.player.head.y += self.velocity * -math.cos(self._player.angle)

        if self._invisible_ticks > 0:
            self._invisible_ticks -= 1
            if self._invisible_ticks == 0:
                self._visible_ticks = 1000  # TODO: Add randomness
        else:

            if not self._check_player_collision(game_state):
                return False  # TODO: Maybe the last point should be added
            if not self._check_for_wall_collision(game_state):
                return False

            self.player.body[len(self.player.body) - 1] \
                .append(Point(self.player.head.x, self.player.head.y))

            if self._visible_ticks > 0:
                self._visible_ticks -= 1
                if self._visible_ticks == 0:
                    # Now this player is invisible
                    self._player.body.append(list())
                    self._invisible_ticks = ServerConstants.HOLE_DURATION

        return True
