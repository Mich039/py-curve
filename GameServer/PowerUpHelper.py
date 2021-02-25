import copy

from GameObjects.Point import Point
from GameObjects.PowerUp import PowerUp
from GameObjects.PowerUpType import PowerUpType
from GameServer import PowerUpConstants


def create_power_up(type: PowerUpType, location: Point) -> PowerUp:
    """
    Creates a power up of the given type and location. The total ticks will be set according to type

    :param type: The power up type
    :param location: The location in the arena
    :return: The new power up object
    """
    new_power_up: PowerUp = PowerUp()
    new_power_up.location = location
    new_power_up.power_up_type = type
    new_power_up.ticks_left = PowerUpConstants.POWER_UP_TICKS[type]
    return new_power_up


def duplicate_power_up(power_up: PowerUp) -> PowerUp:
    """
    Copies the powerup

    :param power_up: The power up to be copied
    :return: The newly created power up
    """
    return copy.copy(power_up)


def is_enemy_power_up(power_up: PowerUp) -> bool:
    """
    Checks if the power up is meant for the other players

    :param power_up: The power up in question
    :return: True if it is an 'Enemy power up'
    """
    return power_up.power_up_type in [PowerUpType.ENEMY_CORNER, PowerUpType.ENEMY_INVERSE]


def is_global_power_up(power_up: PowerUp) -> bool:
    """
    Checks if the power up is a power up that affects the game state, not the players

    :param power_up: The power up in question
    :return: True if it is an 'Global PowerUp'
    """
    return power_up.power_up_type in [PowerUpType.CLEAR]
