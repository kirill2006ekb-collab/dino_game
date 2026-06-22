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
flockbird_width = 45
flockbird_height = 40

#Min/Max параметры
MIN_DELAY_LIMIT = 20
MIN_SPAWN_DELAY = 75
MAX_SPAWN_DELAY = 150
min_speed = 5.0
max_speed = 15.0
max_score = 5000.0
SCORE_CHECK_OFFSET = 10

#ПАРАМЕТРЫ ПТИЦ (препятствия)
BIRD_MAX_Y = GROUND_Y - bird_height - 70 #верхняя граница
BIRD_MIN_Y = GROUND_Y - bird_height - 5 #нижняя граница
BIRD_ANIMATION_SPEED = 25
BIRD_VX_MIN = 0.25
BIRD_VX_MAX = 0.75
BIRD_VY_MIN = -0.5
BIRD_VY_MAX = 0.5

#ПАРАМЕТРЫ СТАИ (визуальный эффект)
FLOCKBIRD_VX_MIN = 0.5
FLOCKBIRD_VX_MAX = 2
FLOCK_BIRD_ANIMATION_SPEED = 12
FLOCK_SIZE_MIN = 1
FLOCK_SIZE_MAX = 4
FLOCK_SPEED_MULTIPLIER = 1.5
FLOCKBIRD_MAX_Y = GROUND_Y - flockbird_height - 300 #верхняя граница
FLOCKBIRD_MIN_Y = GROUND_Y - flockbird_height - 150 #нижняя граница
max_flockbird_speed = 4.0
min_flockbird_speed = 2.0
perception_radius = 150  # радиус, в котором видит соседей
SEPARATION_DIST = 60

#ВЕСА ПРАВИЛ
separation_weight = 0.2
alignment_weight = 0.06
cohesion_weight = 0.001

#PRD
C_percents = {5:0.0038,
              10:0.0147,
              15:0.0322,
              20:0.0557,
              25:0.0844,
              30:0.1189,
              35:0.1594,
              40:0.2096,
              45:0.2866,
              50:0.3286,
              55:0.3843,
              60:0.4478,
              65:0.4974,
              70:0.5643,
              75:0.6710}

