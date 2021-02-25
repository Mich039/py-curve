# define default thickness for drawing lines (must be odd)
from GameObjects.PowerUpType import PowerUpType

LINE_THICKNESS = 3
# define diameter of head, should be close to LINE_THICKNESS
HEAD_RADIUS = 3
BACKGROUND_COLOR = (30, 30, 30)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

POWER_UP_RADIUS = 15
POWER_UP_COLORS = {
    PowerUpType.SLOW: (255, 50, 50),
    PowerUpType.SPEED: (50, 255, 50),
    PowerUpType.FLYING: (50, 50, 255),
    PowerUpType.CLEAR: (255, 105, 180),
    PowerUpType.ENEMY_INVERSE: (50, 50, 255),
    PowerUpType.CORNER: (55, 0, 0),
    PowerUpType.ENEMY_CORNER: (50, 50, 255)
}