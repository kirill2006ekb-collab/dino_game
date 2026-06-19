# config.py

# Размеры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_Y = SCREEN_HEIGHT - 50  # 350

# Физика
GRAVITY = 0.5
JUMP_STRENGTH = -10

# Игровые параметры
FPS = 60

# Цвета
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255)
}

# Названия событий
EVENT_RETURN_TO_POOL = "return_to_pool"
EVENT_DINO_JUMP = "dino_jump"
EVENT_DINO_DUCK_START = "dino_duck_start"
EVENT_DINO_DUCK_STOP = "dino_duck_stop"
EVENT_GAME_RESET = "game_reset"
EVENT_COLLISION = "collision"
EVENT_OBSTACLE_PASSED = "obstacle_passed"


#Размеры
dino_width = 50
dino_height = 50
big_cactus_width = 30
big_cactus_height = 60
small_cactus_width = 25
small_cactus_height = 45
bird_width = 50
bird_height = 45


MIN_DELAY_LIMIT = 20
MIN_SPAWN_DELAY = 75
MAX_SPAWN_DELAY = 150
min_speed = 5.0
max_speed = 15.0
max_score = 5000.0