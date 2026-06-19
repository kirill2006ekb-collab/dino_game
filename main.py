import pygame
import sys
import random
from config import *
from events import EventBus
from models import GameModel, Cactus, Bird
from views import GameView
from controllers import InputController, GameController
from patterns import ObjectPool, ObstacleFactory


class Game:
    
    def __init__(self):
        
        # инициализация pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#pygame.FULLSCREEN
        pygame.display.set_caption("Dino Game")
        self.clock = pygame.time.Clock()
        
        # Model — данные и логика
        self.model = GameModel()
        
        # View — отрисовка
        self.view = GameView(self.screen)
        
        # EventBus — Singleton, получаем экземпляр
        self.event_bus = EventBus()
        
        # Пул для маленьких кактусов (10 штук)
        self.small_cactus_pool = ObjectPool(
            Cactus, 10,
            x=SCREEN_WIDTH, cactus_type=1
        )
        
        # Пул для больших кактусов (7 штук)
        self.big_cactus_pool = ObjectPool(class_type=Cactus, size=7, x=SCREEN_WIDTH, cactus_type=2)
        
        # Пул для птиц (7 штук)
        self.bird_pool = ObjectPool(
            Bird, 7,
            x=SCREEN_WIDTH
        )
        
        # Создание контроллера, ему нужны пулы для возврата объектов
        self.game_controller = GameController(
            self.model, 
            self.small_cactus_pool,
            self.big_cactus_pool,
            self.bird_pool
        )
        self.input_controller = InputController()
        
        # Подписываемся на коллизию для остановки игры
        self.event_bus.subscribe(EVENT_COLLISION, self._on_collision)
        
        self.spawn_timer = 0      # Счётчик кадров до следующего спавна
        self.running = True       # Флаг работы игры
    
    def _on_collision(self, _):
        self.model.is_running = False
        print("[Game] СТОЛКНОВЕНИЕ! Игра остановлена. Нажмите R для перезапуска")
    
    def _spawn_obstacle(self):

        score = self.model.score
        
        # Фабрика выбирает тип препятствия
        obstacle_type = ObstacleFactory.get_random_type(score)
        
        # Берём объект из соответствующего пула
        obstacle = None
        
        if obstacle_type == 'small_cactus':
            obstacle = self.small_cactus_pool.acquire()
            if obstacle:
                print(f"[Game] Спавн маленького кактуса #{obstacle.id}, в пуле осталось: {len(self.small_cactus_pool._pool)}")
        
        elif obstacle_type == 'big_cactus':
            obstacle = self.big_cactus_pool.acquire()
            if obstacle:
                print(f"[Game] Спавн большого кактуса #{obstacle.id}, в пуле осталось: {len(self.big_cactus_pool._pool)}")
        
        elif obstacle_type == 'bird':
            obstacle = self.bird_pool.acquire()
            if obstacle:
                print(f"[Game] Спавн птицы #{obstacle.id}, в пуле осталось: {len(self.bird_pool._pool)}")
        
        # Если объект успешно получен — настраиваем и добавляем
        if obstacle:
            obstacle.speed = self.model.game_speed
            obstacle.x = SCREEN_WIDTH  # Появляется с правого края
            obstacle.is_active = True
            self.model.add_obstacle(obstacle)
        else:
            print(f"[Game] ВНИМАНИЕ: Не удалось создать препятствие типа {obstacle_type} — пул пуст!")
    
    def update(self):
        if not self.model.is_running or not self.model.dino.is_alive:
            return
        
        # Обновляем логику через контроллер
        self.game_controller.update()
        
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
        print("\n[Game] Игровой цикл запущен")
        
        while self.running:
            self.running = self.handle_events()
            
            self.update()
            
            self.render()
            
            self.clock.tick(FPS)
        
        # Выход из игры
        self._cleanup()
    
    def _cleanup(self):
        print("\n[Game] Завершение игры...")
        
        # Возвращаем все активные препятствия в пулы
        for obstacle in self.model.obstacles[:]:
            if isinstance(obstacle, Cactus):
                if obstacle.cactus_type == 1:
                    self.small_cactus_pool.release(obstacle)
                else:
                    self.big_cactus_pool.release(obstacle)
            elif isinstance(obstacle, Bird):
                self.bird_pool.release(obstacle)
        
        print("[Game] Все ресурсы освобождены")
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()