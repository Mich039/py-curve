import math
import random
from typing import List, Optional

import GameObjects.Player as Player
from GameObjects.Point import Point
from GameObjects.PowerUp import PowerUp
from GameObjects.PowerUpType import PowerUpType
from GameServer import PowerUpHelper
from GameServer.CollisionDetectionHelper import check_collision, is_relevant
from GameServer.GameServerWrappers.ListSegment import ListSegment
from GameServer.GameServerWrappers.PlayerInputWrapper import PlayerInputWrapper
import GameServer.ServerConstants as ServerConstants


class PlayerWrapper:

    def __init__(self, player: Player):
        self._player: Player = player
        self._invisible_ticks: int = 0
        self._visible_ticks: int = PlayerWrapper._random_time_visible()
        self._velocity: float = ServerConstants.BASE_SPEED
        self._body: List[ListSegment] = [ListSegment(), ]

    def get_wrapped_player(self) -> Player:
        """
        Converts the Playerwrapper to a Player Object that will be sent to the client
        :return: The current Player
        """
        self._player.body = [segment.list for segment in self._body]
        return self._player

    @property
    def player(self) -> Player:
        return self._player

    @player.setter
    def player(self, value: Player):
        self._player = value

    @property
    def body(self) -> List[ListSegment]:
        return self._body

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

    @property
    def velocity(self) -> float:
        return self._velocity

    @velocity.setter
    def velocity(self, value: float):
        self._velocity = value

    def reset_score(self):
        """
        Resets the score of the player to Zero
        """
        self._player.score.deaths = 0
        self._player.score.score_points = 0
        self._player.score.power_up_points = 0

    def init_position(self, pos: Point, angle: float):
        """
        Resets the body of the player and sets the start location

        :param pos: The Position the player will start from
        :param angle: The angle that the player will get set at
        """
        self._player.head = pos
        self._player.angle = angle
        # Remove Body
        self.clear_body()

    def rotate_by(self, deg):
        """
        Rotates the player

        :param deg: The angle in degrees the player will be rotated clockwise
        """
        self.player.angle += math.radians(deg)

    def _check_player_collision(self, game_state) -> bool:
        """
        Checks if the player collided with some other body and returns the result

        :param game_state: The GameStateWrapper with the arena info
        :return: If a collision occurred False is returned. If no collision occurred True is returned instead
        """
        # Loop over all segments in all other players
        for player in game_state.player_list.values():
            for segment in [segment for segment in player.body if segment.point_in_segment(self.player.head)]:
                count = 0
                starting_point = None
                last_point = None
                for point in segment.list:
                    count = count + 1
                    # Skip every other point. The line that will get checked is longer and the performance is better
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
                            # Calculate the normal vector to check the collision of a plus shape
                            first_perpendicular_vec = Point(-(self.player.head.y - previous_point.y),
                                                            (self.player.head.x - previous_point.x))
                            factor = 1 / math.sqrt(first_perpendicular_vec.x ** 2 + first_perpendicular_vec.y ** 2)
                            first_point = Point(
                                self.player.head.x + factor * ServerConstants.PLAYER_WIDTH_RADIUS * first_perpendicular_vec.x,
                                self.player.head.y + factor * ServerConstants.PLAYER_WIDTH_RADIUS * first_perpendicular_vec.y)
                            second_point = Point(
                                self.player.head.x + factor * -ServerConstants.PLAYER_WIDTH_RADIUS * first_perpendicular_vec.x,
                                self.player.head.y + factor * -ServerConstants.PLAYER_WIDTH_RADIUS * first_perpendicular_vec.y)
                            if check_collision(first_point, second_point, last_point, point) or check_collision(
                                    self.player.head, previous_point, last_point, point):
                                return False
                    last_point = point
        return True

    def _check_for_wall_collision(self, game_state) -> bool:
        """
        Checks if the player hit the outside wall

        :param game_state: The gamestate holding the all the game info
        :return: If a wall is hit False is returned, other True
        """
        return not (
                self._player.head.x >= ServerConstants.PLAY_AREA_SIZE or self._player.head.x <= 0 or self._player.head.y >= ServerConstants.PLAY_AREA_SIZE or self._player.head.y <= 0)

    def _check_for_power_up_collision(self, game_state) -> Optional[PowerUp]:
        """
        Checks if the player collided with a power up

        :param game_state: The game state with the current ground power ups in it
        :return: The power up the player collided with. Otherwise None
        """
        for power_up in game_state.ground_power_up:
            if (self.player.head.x - power_up.location.x) ** 2 + (
                    self.player.head.y - power_up.location.y) ** 2 <= ServerConstants.POWER_UP_RADIUS ** 2:
                # We got one boys!
                return power_up
        return None

    @staticmethod
    def _random_time_visible() -> int:
        """
        Randomly generates the amount of ticks the player will be visible
        :return: The amount of ticks visible
        """
        return math.trunc(random.uniform(ServerConstants.MIN_TICKS_VISIBLE, ServerConstants.MAX_TICKS_VISIBLE))

    def _calculate_rotation(self, input: PlayerInputWrapper) -> float:
        """
        Calculates the angle of rotation for one tick.
        Is the Corner PowerUp active, the angle will be 90/-90 and will only activate one per new input.
        Is the Inverted Power active, the angle will be flipped so left will be right and the opposite.
        :param input: The input for which the angle should be calculated.
        :return: If no input is active 0. Otherwise the angle clockwise.
        """
        rotation: float = 0

        if self._is_square():
            if input.left and not input.processed:
                rotation = -90
            if input.right and not input.processed:
                rotation = 90
        else:
            if input.left:
                rotation = -ServerConstants.ROTATION_SPEED
            if input.right:
                rotation = ServerConstants.ROTATION_SPEED

        if self._is_inverted():
            rotation *= -1
        return rotation

    def move(self, input: PlayerInputWrapper, game_state) -> bool:
        """
        Tries to rotate and afterwards move the player head "forward". This method also checks for power up collisions
        and sets the power up accordingly.
        :param input: The Player input used for the calculations
        :param game_state: The game state will all the game information
        :return: If the move was not successful False is returned.
        """
        rotation: float = self._calculate_rotation(input)
        if not rotation == 0:
            self.rotate_by(rotation)

        mult: float = self._get_current_speed_multiplier()

        self.player.head.x += self.velocity * mult * math.sin(self._player.angle)
        self.player.head.y += self.velocity * mult * -math.cos(self._player.angle)

        # Check for Power Ups and handle them accordingly
        collected_power_up: Optional[PowerUp] = self._check_for_power_up_collision(game_state)
        if collected_power_up is not None:
            game_state.ground_power_up.remove(collected_power_up)
            if PowerUpHelper.is_enemy_power_up(collected_power_up):
                for player in [player for player in game_state.player_list.values() if
                               not player.player.id == self.player.id]:
                    player.player.active_power_ups.append(PowerUpHelper.duplicate_power_up(collected_power_up))
            elif PowerUpHelper.is_global_power_up(collected_power_up):
                if collected_power_up.power_up_type == PowerUpType.CLEAR:
                    for player in game_state.player_list.values():
                        player.clear_body()
            else:
                self._player.active_power_ups.append(collected_power_up)
                if collected_power_up.power_up_type == PowerUpType.FLYING:
                    # When the player starts flying the body creates a big hole
                    self._body.append(ListSegment())

        if self._invisible_ticks > 0:
            self._invisible_ticks -= 1
            if self._invisible_ticks <= 0:
                self._visible_ticks = PlayerWrapper._random_time_visible()
        else:

            # Check for collisions with player bodies
            if not self._check_player_collision(game_state) and not self._is_flying():
                return False
            # Check for collisions with walls
            if not self._check_for_wall_collision(game_state):
                return False

            # If the player is flying don't add to the body.
            if not self._is_flying():
                self._body[len(self._body) - 1].add_point(Point(self.player.head.x, self.player.head.y))

            # If the player is visible remove from the visible counter until it is 0. Then the player will turn
            # invisible.
            if self._visible_ticks > 0:
                self._visible_ticks -= 1
                if self._visible_ticks <= 0:
                    # Now this player is invisible
                    self._body.append(ListSegment())
                    self._invisible_ticks = ServerConstants.HOLE_DURATION

        return True

    def clear_body(self):
        """
        Removes the body of the player by setting it to the initial state
        """
        self._body = [ListSegment(), ]

    def _get_current_speed_multiplier(self) -> float:
        """
        Calculates the speed multiplier of all active power ups
        :return: The multiplier. If no powerups are active this is 1.0
        """
        multiplier: float = 1.0
        for power_up in self._player.active_power_ups:
            if power_up.power_up_type in (PowerUpType.SPEED,):
                multiplier *= ServerConstants.SPEED_MULTIPLIER
            elif power_up.power_up_type in (PowerUpType.SLOW,):
                multiplier /= ServerConstants.SPEED_MULTIPLIER
        return multiplier

    def _is_inverted(self) -> bool:
        """
        Checks if the player has an active inverted Power up
        :return: True if the player has an active inverted power up
        """
        return PowerUpType.ENEMY_INVERSE in (p.power_up_type for p in self._player.active_power_ups)

    def _is_square(self) -> bool:
        """
        Checks if the player has an active CORNER Power up
        :return: True if the player has an active CORNER power up
        """
        return PowerUpType.ENEMY_CORNER in (p.power_up_type for p in self._player.active_power_ups) \
            or PowerUpType.CORNER in (p.power_up_type for p in self._player.active_power_ups)

    def _is_flying(self) -> bool:
        """
        Checks if the player has an active FLYING Power up
        :return: True if the player has an active FLYING power up
        """
        return PowerUpType.FLYING in (p.power_up_type for p in self._player.active_power_ups)

    def power_up_tick(self):
        """
        Ticks down the ticks of active power up.
        If the counter is expired, the power up will get removed.
        """
        expired_power_ups = []
        for power_up in self._player.active_power_ups:
            power_up.ticks_left -= 1
            if power_up.ticks_left < 0:
                expired_power_ups.append(power_up)
        for power_up_to_remove in expired_power_ups:
            self._player.active_power_ups.remove(power_up_to_remove)
