from GameObjects.PowerUpType import PowerUpType

# The live time of a power up once it is activated. The given amount is ticks alive
POWER_UP_TICKS = {
    PowerUpType.SLOW: 100,
    PowerUpType.SPEED: 100,
    PowerUpType.FLYING: 100,
    PowerUpType.CLEAR: 100,
    PowerUpType.ENEMY_INVERSE: 100,
    PowerUpType.CORNER: 100,
    PowerUpType.ENEMY_CORNER: 100
}