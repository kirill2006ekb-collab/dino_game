from config import *
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
            return True
        return False
    
    def start_ducking(self) -> bool:
        self.is_ducking_key_held = True
        if self.state_machine.state == DinoState.RUNNING and self.is_alive:
            return True
        return False
    
    def stop_ducking(self) -> bool:
        self.is_ducking_key_held = False
        if self.state_machine.state == DinoState.DUCKING and self.is_alive:
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
        
        # Обновляем конечный автомат
        self.state_machine.update()

        if self.state_machine.state == DinoState.DUCKING:
            self.height = dino_height // 1.5
            self.width = dino_width + 10
            self.y = GROUND_Y - self.height
        
        elif self.state_machine.state == DinoState.RUNNING:
            self.height = dino_height
            self.width = dino_width
            self.y = GROUND_Y - self.height

        if self.y + self.height > GROUND_Y:
            self.y = GROUND_Y - self.height
            if self.vel_y > 0:
                self.vel_y = 0
    
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
    
    def die(self):
        self.is_alive = False
        self.state_machine.state = DinoState.DEAD
    
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
        self.y = GROUND_Y - bird_height - random.randint(0, BIRD_MAX_Y)
        self.width = bird_width
        self.height = bird_height
        self.speed = min_speed
        self.is_active = True
        self.has_given_score = False
        self.current_frame = 0
        self.animation_timer = 0
        self.vy = 0
        self.direction_timer=0
        self.vx = random.uniform(BIRD_VX_MIN,BIRD_VX_MAX)
    
    def reset(self):
        self.x = 800
        self.speed = min_speed
        self.is_active = True
        self.has_given_score = False
        self.y = GROUND_Y - bird_height - random.randint(0, BIRD_MAX_Y)
        self.current_frame = 0
        self.animation_timer = 0
        self.vy = 0
        self.direction_timer=0
        self.vx = random.uniform(BIRD_VX_MIN,BIRD_VX_MAX)
    
    def update(self):
        self.direction_timer-=1
        if self.direction_timer<=0:
            self.vy=random.uniform(BIRD_VY_MIN, BIRD_VY_MAX)
            self.direction_timer=random.randint(FPS//2, int(FPS * 1.5))#количество кадров от 0.5 до 1.5 секунд
        self.y += self.vy
        if self.y < BIRD_MAX_Y:
            self.y = BIRD_MAX_Y
            self.vy = abs(self.vy)  # начинаем двигаться вниз
        elif self.y > BIRD_MIN_Y:
            self.y = BIRD_MIN_Y
            self.vy = -abs(self.vy)  # начинаем двигаться вверх

        self.x -= self.speed
        self.animation_timer += 1
        if self.animation_timer >= BIRD_ANIMATION_SPEED:
            self.animation_timer = 0
            self.current_frame = 1 - self.current_frame
    
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
    
    def is_offscreen(self):
        return self.x + self.width <= 0
    

class FlockBird:
    
    def __init__(self, x=800, flock=None):
        self.id = 0
        self.x = x
        self.reset_y()
        self.width = flockbird_width
        self.height = flockbird_height
        self.speed = min_speed
        self.is_active = True
        self.current_frame = 0
        self.animation_timer = 0

        self.vx = -random.uniform(FLOCKBIRD_VX_MIN, FLOCKBIRD_VX_MAX)
        self.vy = random.uniform(BIRD_VY_MIN, BIRD_VY_MAX)
                
        # Ссылка на всех птиц в стае
        if flock:
            self.flock = flock
        else:
            self.flock = []
    
    def reset(self):
        self.x = 800
        self.vx = -random.uniform(FLOCKBIRD_VX_MIN, FLOCKBIRD_VX_MAX)
        self.vy = random.uniform(BIRD_VY_MIN, BIRD_VY_MAX)
        self.speed = min_speed
        self.is_active = True
        self.current_frame = 0
        self.animation_timer = 0
    
    def update(self):
        neighbors = self._get_neighbors()

        if neighbors:
            separation = self._separation(neighbors)
            alignment = self._alignment(neighbors)
            cohesion = self._cohesion(neighbors)

            # Применяем силы к скорости
            self.vx += separation[0] * separation_weight
            self.vy += separation[1] * separation_weight
            self.vx += alignment[0] * alignment_weight
            self.vy += alignment[1] * alignment_weight
            self.vx += cohesion[0] * cohesion_weight
            self.vy += cohesion[1] * cohesion_weight

        speed = (self.vx**2 + self.vy**2)**0.5
        if speed > max_flockbird_speed:
            self.vx = (self.vx / speed) * max_flockbird_speed
            self.vy = (self.vy / speed) * max_flockbird_speed #нормализуем вектор vx и vy приравниваем его значение к max_flockbird_speed
        elif speed < min_flockbird_speed and speed != 0:
            self.vx = (self.vx / speed) * min_flockbird_speed
            self.vy = (self.vy / speed) * min_flockbird_speed #нормализуем вектор vx и vy приравниваем его значение к min_flockbird_speed

        self.x += self.vx
        self.y += self.vy

        if self.y < FLOCKBIRD_MAX_Y:
            self.y = FLOCKBIRD_MAX_Y
            self.vy = abs(self.vy)
        elif self.y > FLOCKBIRD_MIN_Y:
            self.y = FLOCKBIRD_MIN_Y
            self.vy = -abs(self.vy)
        
        self.x -= self.speed

        self.animation_timer += 1
        if self.animation_timer >= FLOCK_BIRD_ANIMATION_SPEED:
            self.animation_timer = 0
            self.current_frame = 1 - self.current_frame
    
    def _get_neighbors(self):
        neighbors = []
        for bird in self.flock:
            dist = ((self.x - bird.x)**2 + (self.y - bird.y)**2)**0.5
            if dist < perception_radius:
                neighbors.append(bird)
        return neighbors

    def _separation(self, neighbors):
        """Разделение — отталкивание от соседей"""
        dx, dy = 0, 0
        for bird in neighbors:
            dist = ((self.x - bird.x)**2 + (self.y - bird.y)**2)**0.5
            if dist < SEPARATION_DIST:
                dx += (self.x - bird.x) / (dist + 0.001) #0.001 - защита от деления на 0
                dy += (self.y - bird.y) / (dist + 0.001)
        return dx, dy #вектора силы
    
    def _alignment(self, neighbors):
        """Выравнивание — движение в ту же сторону"""
        avg_vx, avg_vy = 0, 0
        for bird in neighbors:
            avg_vx += bird.vx
            avg_vy += bird.vy
        if neighbors:
            avg_vx /= len(neighbors)
            avg_vy /= len(neighbors)
        return avg_vx, avg_vy #средние vx и vy - средняя скорость
    
    def _cohesion(self, neighbors):
        """Сплочённость — движение к центру стаи"""
        cx, cy = 0, 0
        for bird in neighbors:
            cx += bird.x
            cy += bird.y
        if neighbors:
            cx /= len(neighbors)
            cy /= len(neighbors) #средние x и y - центр масс
        return cx - self.x, cy - self.y #вектор к центру стаи
    
    def reset_y(self):
        self.y = GROUND_Y - bird_height - random.randint(FLOCKBIRD_MAX_Y, FLOCKBIRD_MIN_Y)

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
    
    def is_offscreen(self):
        return self.x + self.width <= 0


class Flock:
    """Стая птиц — визуальный эффект"""
    
    def __init__(self, flock_bird_pool, game_speed):
        self.flock_bird_pool = flock_bird_pool
        self.all_birds = []
        self.create_flock(game_speed)
    
    def create_flock(self, game_speed):
        flock_size = random.randint(FLOCK_SIZE_MIN, FLOCK_SIZE_MAX)
        
        for i in range(flock_size):
            bird = self.flock_bird_pool.acquire()
            bird.reset_y()
            if not bird:
                break
            
            bird.speed = game_speed * FLOCK_SPEED_MULTIPLIER
            bird.x = SCREEN_WIDTH + random.randint(0, 100)
            self.all_birds.append(bird)

        for bird in self.all_birds:
            bird.flock = [i for i in self.all_birds if i != bird]

        
    
    def get_all_birds(self):
        return self.all_birds
    
    def is_completely_offscreen(self):
        for bird in self.all_birds:
            if not bird.is_offscreen():
                return False
        return True


class GameModel:
    
    def __init__(self):
        self.bird_prd = PRD(30, "bird")
        self.flock_prd = PRD(15, "flock")
        self.big_cactus_prd = PRD(35, "big_cactus")
        self.nothing_prd = PRD(5, "nothing")
        self.dino = DinoModel()
        self.obstacles = []
        self.flocks = []
        self.score = 0
        self.game_speed = min_speed
        self.is_running = True
        self.passed_obstacles = set()
        self.ground_offset = 0.0
    
    def reset(self):
        self.flock_prd.reset()
        self.bird_prd.reset()
        self.big_cactus_prd.reset()
        self.nothing_prd.reset()
        self.dino.reset()
        self.obstacles.clear()
        self.score = 0
        self.game_speed = min_speed
        self.is_running = True
        self.passed_obstacles.clear()
        self.ground_offset = 0.0
    
    def update_score(self):
        self.score += SCORE_CHECK_OFFSET
        
        progress = min(1.0, self.score / max_score)
        self.game_speed = min_speed + progress * (max_speed - min_speed)
        for obstacle in self.obstacles:
            if not isinstance(obstacle,FlockBird):
                obstacle.speed = self.game_speed
                if isinstance(obstacle,Bird):
                    obstacle.speed+=obstacle.vx
    
    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)
    
    def remove_obstacle(self, obstacle):
        if obstacle in self.obstacles:
            self.obstacles.remove(obstacle)
    
    def add_flock(self, flock):
        self.flocks.append(flock)
        for bird in flock.get_all_birds():
            self.obstacles.append(bird)
    
    def remove_flock(self, flock):
        if flock in self.flocks:
            self.flocks.remove(flock)
    
    def clear_flocks(self):
        self.flocks = []

    def is_obstacle_passed(self, obstacle_id):
        return obstacle_id in self.passed_obstacles
    
    def mark_obstacle_passed(self, obstacle_id):
        self.passed_obstacles.add(obstacle_id)
    
    def update_ground_offset(self):
        self.ground_offset += self.game_speed