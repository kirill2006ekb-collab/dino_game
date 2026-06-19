from config import GROUND_Y, GRAVITY, JUMP_STRENGTH, dino_height, dino_width, bird_height, bird_width, big_cactus_height, big_cactus_width, small_cactus_height, small_cactus_width, min_speed, max_speed, max_score
from patterns import StateMachine, DinoState, PRD
import random


class DinoModel:
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = 80
        self.y = GROUND_Y - dino_height
        self.vel_y = 0
        self.width = dino_width
        self.height = dino_height
        self.is_alive = True
        self.is_ducking_key_held = False
        
        self.state_machine = StateMachine(DinoState.RUNNING)
        self._setup_state_machine()
    
    def _setup_state_machine(self):
        
        def is_on_ground():
            return self.y + self.height >= GROUND_Y
        
        def is_duck_key_released():
            return not self.is_ducking_key_held
        
        def is_duck_key_held():
            return self.is_ducking_key_held
        
        self.state_machine.add_transition(
            DinoState.JUMPING, DinoState.RUNNING, is_on_ground
        )
        
        self.state_machine.add_transition(
            DinoState.DUCKING, DinoState.RUNNING, is_duck_key_released
        )

        self.state_machine.add_transition(
            DinoState.RUNNING, DinoState.DUCKING, is_duck_key_held
        )
    
    def jump(self) -> bool:
        if self.state_machine.state == DinoState.RUNNING and self.is_alive:
            self.vel_y = JUMP_STRENGTH
            self.state_machine.state = DinoState.JUMPING
            print(f"[Dino] Прыжок! y={self.y}")
            return True
        return False
    
    def start_ducking(self) -> bool:
        self.is_ducking_key_held = True
        if self.state_machine.state == DinoState.RUNNING and self.is_alive:
            print(f"[Dino] Начал приседать, высота={self.height}")
            return True
        return False
    
    def stop_ducking(self) -> bool:
        self.is_ducking_key_held = False
        if self.state_machine.state == DinoState.DUCKING and self.is_alive:
            print(f"[Dino] Прекратил приседать")
            return True
        return False
    
    def update(self):
        if not self.is_alive:
            return
        
        # Логика прыжка
        if self.state_machine.state == DinoState.JUMPING:
            self.vel_y += GRAVITY
            self.y += self.vel_y
            
            if self.y + self.height >= GROUND_Y:
                self.y = GROUND_Y - self.height
                self.vel_y = 0
                self.state_machine.state = DinoState.RUNNING
                print(f"[Dino] Приземлился!")
        
        # Обновляем конечный автомат
        self.state_machine.update()

        if self.state_machine.state == DinoState.DUCKING:
            self.height = dino_height // 1.5
            self.width = dino_width + 10   # можно оставить или убрать – на ваше усмотрение
            self.y = GROUND_Y - self.height
        
        elif self.state_machine.state == DinoState.RUNNING:
            self.height = dino_height
            self.width = dino_width
            self.y = GROUND_Y - self.height

        if self.y + self.height > GROUND_Y:
            self.y = GROUND_Y - self.height
            if self.vel_y > 0:
                self.vel_y = 0
                print(f"[Dino] Принудительная фиксация на земле, y={self.y}")
    
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
    
    def die(self):
        self.is_alive = False
        self.state_machine.state = DinoState.DEAD
        print(f"[Dino] Погиб!")
    
    def __repr__(self):
        return f"Dino(state={self.state_machine.state.name}, y={self.y}, vy={self.vel_y}, duck_key={self.is_ducking_key_held})"


class Cactus:
    
    def __init__(self, x=800, y=GROUND_Y-small_cactus_height, cactus_type=1):
        self.id = 0
        self.x = x
        self.y = y
        self.cactus_type = cactus_type
        self.speed = min_speed
        self.is_active = True
        self.has_given_score = False
        self.cactus_picture = None
        
        if cactus_type == 1:  # Маленький
            self.width = small_cactus_width
            self.height = small_cactus_height
        else:  # Большой
            self.width = big_cactus_width
            self.height = big_cactus_height
            self.y = GROUND_Y - self.height
    
    def reset(self):
        self.x = 800
        self.speed = min_speed
        self.is_active = True
        self.has_given_score = False
    
    def update(self):
        self.x -= self.speed
    
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
    
    def is_offscreen(self):
        return self.x + self.width <= 0
    
    def __repr__(self):
        return f"Cactus(id={self.id}, x={self.x}, type={self.cactus_type}, height={self.height})"


class Bird:
    
    def __init__(self, x=800):
        self.id = 0
        self.x = x
        self.y = GROUND_Y - bird_height - random.randint(0, 60)
        self.width = bird_width
        self.height = bird_height
        self.speed = min_speed
        self.is_active = True
        self.has_given_score = False
        self.current_frame = 0
        self.animation_timer = 0
    
    def reset(self):
        self.x = 800
        self.speed = min_speed
        self.is_active = True
        self.has_given_score = False
        self.y = GROUND_Y - bird_height - random.randint(0, 60)
        self.current_frame = 0
        self.animation_timer = 0
    
    def update(self):
        self.x -= self.speed
        self.animation_timer += 1
        if self.animation_timer >= 30:
            self.animation_timer = 0
            self.current_frame = 1 - self.current_frame
    
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
    
    def is_offscreen(self):
        return self.x + self.width <= 0
    
    def __repr__(self):
        return f"Bird(id={self.id}, x={self.x}, score_given={self.has_given_score})"


class GameModel:
    
    def __init__(self):
        self.bird_prd = PRD(20, "bird")
        self.big_cactus_prd = PRD(30, "big_cactus")
        self.nothing_prd = PRD(5, "nothing")
        self.dino = DinoModel()
        self.obstacles = []
        self.score = 0
        self.game_speed = min_speed
        self.is_running = True
        self.passed_obstacles = set()
        print("[GameModel] Инициализирована")
    
    def reset(self):
        self.dino.reset()
        self.obstacles.clear()
        self.score = 0
        self.game_speed = min_speed
        self.is_running = True
        self.passed_obstacles.clear()
        print("[GameModel] Игра сброшена")
    
    def update_score(self, points=10):
        self.score += points
        
        progress = min(1.0, self.score / max_score)
        self.game_speed = min_speed + progress * (max_speed - min_speed)
        for obstacle in self.obstacles:
            obstacle.speed = self.game_speed
        print(f"[GameModel] Счёт={self.score}, скорость={self.game_speed:.2f}")
    
    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)
        print(f"[GameModel] Добавлено препятствие: {obstacle}")
    
    def remove_obstacle(self, obstacle):
        if obstacle in self.obstacles:
            self.obstacles.remove(obstacle)
            print(f"[GameModel] Удалено препятствие: {obstacle}")
    
    def is_obstacle_passed(self, obstacle_id):
        return obstacle_id in self.passed_obstacles
    
    def mark_obstacle_passed(self, obstacle_id):
        self.passed_obstacles.add(obstacle_id)
    
    def __repr__(self):
        return f"GameModel(score={self.score}, speed={self.game_speed:.2f}, obstacles={len(self.obstacles)})"