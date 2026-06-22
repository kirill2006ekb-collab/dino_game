import pygame
import sys
import random
from config import *
from events import EventBus
from models import *
from views import GameView
from controllers import InputController, GameController
from patterns import *


class Step():
    def __init__(self,sound,chance):
        self.sound = sound
        self.sound.set_volume(step_volume)
        self.prd = PRD(chance)


class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.sounds['jump'] = pygame.mixer.Sound(SOUND_JUMP)
        self.sounds['lose'] = pygame.mixer.Sound(SOUND_LOSE)
        self.sounds['landing'] = pygame.mixer.Sound(SOUND_LAND)
        self.sounds['flock'] = pygame.mixer.Sound(SOUND_FLOCK)
        pygame.mixer.music.load(SOUND_MUSIC)
        pygame.mixer.music.set_volume(music_volume)
        self.sounds['landing'].set_volume(landing_volume)
        self.sounds['lose'].set_volume(lose_volume)
        self.sounds['jump'].set_volume(jump_volume)
        self.sounds['flock'].set_volume(flock_volume)
        self.music_is_playing = False
        self.steps = []
        for i in steps:
            self.steps.append(Step(pygame.mixer.Sound(i),20))

    
    def play_music(self):
        if not self.music_is_playing:
            pygame.mixer.music.play(-1)
            self.music_is_playing = True

    def stop_music(self):
        if self.music_is_playing:
            pygame.mixer.music.stop()
            self.music_is_playing = False

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def step(self):
        selected = random_prd(self.steps)
        if selected:
            selected.sound.play()


class Game:
    
    def __init__(self):
        
        # инициализация pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#pygame.FULLSCREEN
        pygame.display.set_caption("Dino Game")
        self.clock = pygame.time.Clock()

        self.sound_manager = SoundManager()

        # EventBus — Singleton, получаем экземпляр
        self.event_bus = EventBus()

        # Model — данные и логика
        self.model = GameModel(self.event_bus)
        
        # View — отрисовка
        self.view = GameView(self.screen,self.event_bus)
        
        # Пул для маленьких кактусов
        self.small_cactus_pool = ObjectPool(
            Cactus, 10,
            x=SCREEN_WIDTH, cactus_type=1
        )
        
        # Пул для больших кактусов
        self.big_cactus_pool = ObjectPool(class_type=Cactus, size=7, x=SCREEN_WIDTH, cactus_type=2)
        
        # Пул для птиц в стае
        self.flock_bird_pool = ObjectPool(FlockBird, 15, x=SCREEN_WIDTH)

        # Пул для птиц
        self.bird_pool = ObjectPool(
            Bird, 7,
            x=SCREEN_WIDTH
        )
        
        # Создание контроллера, ему нужны пулы для возврата объектов
        self.game_controller = GameController(
            self.model, 
            self.small_cactus_pool,
            self.big_cactus_pool,
            self.bird_pool,
            self.flock_bird_pool,
            self.sound_manager
        )
        self.input_controller = InputController()
        
        # Подписываемся на коллизию для остановки игры
        self.event_bus.subscribe(EVENT_COLLISION, self._on_collision)
        
        self.spawn_timer = 0      # Счётчик кадров до следующего спавна
        self.running = True       # Флаг работы игры
    
    def _on_collision(self, _):
        self.model.is_running = False
    
    def _spawn_flock(self):
        self.sound_manager.play('flock')
        flock = Flock(self.flock_bird_pool, self.model.game_speed)
        if not flock.get_all_birds():
            return
        self.model.add_flock(flock)

    def _spawn_obstacle(self):
        model = self.model
        
        if model.flock_prd.check():
            self._spawn_flock()

        # Фабрика выбирает тип препятствия
        obstacle_type = ObstacleFactory.get_random_type(model)
        
        # Берём объект из соответствующего пула
        obstacle = None
        
        if obstacle_type == 'small_cactus':
            obstacle = self.small_cactus_pool.acquire()

        elif obstacle_type == 'big_cactus':
            obstacle = self.big_cactus_pool.acquire()

        elif obstacle_type == 'bird':
            obstacle = self.bird_pool.acquire()
        
        elif obstacle_type == None:
            return
        
        # Если объект успешно получен — настраиваем и добавляем
        if obstacle:
            obstacle.speed = self.model.game_speed
            obstacle.x = SCREEN_WIDTH  # Появляется с правого края
            obstacle.is_active = True
            self.model.add_obstacle(obstacle)
    
    def update(self):
        if not self.model.is_running or not self.model.dino.is_alive:
            return
        
        self.model.update_ground_offset()

        # Обновляем логику через контроллер
        self.game_controller.update()

        for flock in self.model.flocks[:]:
            if flock.is_completely_offscreen():
                for bird in flock.get_all_birds():
                    if bird in self.model.obstacles:
                        self.model.obstacles.remove(bird)
                        self.flock_bird_pool.release(bird)
                self.model.remove_flock(flock)
        
        # Спавним препятствия
        self.spawn_timer += 1

        base_delay = random.randint(MIN_SPAWN_DELAY, MAX_SPAWN_DELAY)
        speed_factor = max(0.2, 1.2 - self.model.game_speed / 10)
        spawn_delay = int(base_delay * speed_factor)
        spawn_delay = max(MIN_DELAY_LIMIT, spawn_delay)

        if self.spawn_timer > spawn_delay:
            self._spawn_obstacle()
            self.spawn_timer = 0

    def render(self):
        self.view.render(self.model)
    
    def handle_events(self) -> bool:
        return self.input_controller.handle_events()
    
    def run(self):
        self.sound_manager.play_music()
        while self.running:
            self.running = self.handle_events()
            
            self.update()
            
            self.render()
            
            self.clock.tick(FPS)
        
        # Выход из игры
        self._cleanup()
    
    def _cleanup(self):
        self.model.clear_flocks()
        # Возвращаем все активные препятствия в пулы
        for obstacle in self.model.obstacles[:]:
            if isinstance(obstacle, Cactus):
                if obstacle.cactus_type == 1:
                    self.small_cactus_pool.release(obstacle)
                else:
                    self.big_cactus_pool.release(obstacle)
            elif isinstance(obstacle, Bird):
                self.bird_pool.release(obstacle)
            elif isinstance(obstacle, FlockBird):
                self.flock_bird_pool.release(obstacle)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()