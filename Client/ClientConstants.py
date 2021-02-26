# define default thickness for drawing lines (must be odd)
from GameObjects.PowerUpType import PowerUpType

# target/server ip/port
IP = "gattinger.ddns.net"
PORT = 4321

# FPS limit
FRAMES_PER_SECOND = 60
# timeout limit in ticks
TIME_OUT_LIMIT = 100
# should be uneven to avoid asymmetrical rendering
LINE_THICKNESS = 5

BACKGROUND_COLOR = (30, 30, 30)

FIELD_INACTIVE_COLOR = (50, 50, 90)
FIELD_ACTIVE_COLOR = (50, 50, 220)

# color constants
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# has to be the same as in server constants
POWER_UP_RADIUS = 15

POWER_UP_COLORS = {
    PowerUpType.SLOW: (255, 50, 50),
    PowerUpType.SPEED: (50, 255, 50),
    PowerUpType.FLYING: (50, 50, 255),
    PowerUpType.CLEAR: (255, 105, 180),
    PowerUpType.ENEMY_INVERSE: (150, 75, 0),
    PowerUpType.CORNER: (55, 0, 0),
    PowerUpType.ENEMY_CORNER: (173, 216, 230)
}