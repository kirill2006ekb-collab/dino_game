import pygame
from events import EventBus
from config import (EVENT_DINO_JUMP, EVENT_DINO_DUCK_START, 
                    EVENT_DINO_DUCK_STOP, EVENT_GAME_RESET, 
                    EVENT_COLLISION)
from models import Cactus, Bird
from patterns import DinoState
from views import ResourceManager, mask_collision


class InputController:
    
    def __init__(self):
        self.event_bus = EventBus()
    
    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.event_bus.emit(EVENT_DINO_JUMP)
                    print("[Input] Нажат SPACE → прыжок")
                
                elif event.key == pygame.K_DOWN:
                    self.event_bus.emit(EVENT_DINO_DUCK_START)
                    print("[Input] Нажат DOWN → начать приседание")
                
                elif event.key == pygame.K_r:
                    self.event_bus.emit(EVENT_GAME_RESET)
                    print("[Input] Нажат R → перезапуск")
                
                elif event.key == pygame.K_ESCAPE:
                    return False
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.event_bus.emit(EVENT_DINO_DUCK_STOP)
                    print("[Input] Отпущен DOWN → прекратить приседание")
        
        return True


class GameController:
    
    def __init__(self, game_model, small_pool, big_pool, bird_pool):
        self.model = game_model
        self.small_pool = small_pool
        self.big_pool = big_pool
        self.bird_pool = bird_pool
        self.event_bus = EventBus()
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        self.event_bus.subscribe(EVENT_DINO_JUMP, self._on_dino_jump)
        self.event_bus.subscribe(EVENT_DINO_DUCK_START, self._on_duck_start)
        self.event_bus.subscribe(EVENT_DINO_DUCK_STOP, self._on_duck_stop)
        self.event_bus.subscribe(EVENT_GAME_RESET, self._on_game_reset)
    
    def _on_dino_jump(self, _):
        self.model.dino.jump()
    
    def _on_duck_start(self, _):
        self.model.dino.start_ducking()
    
    def _on_duck_stop(self, _):
        self.model.dino.stop_ducking()
    
    def _on_game_reset(self, _):
        for obstacle in self.model.obstacles:
            self._return_to_pool(obstacle)   
        self.model.reset()
    
    def _return_to_pool(self, obstacle):
        if isinstance(obstacle, Cactus):
            if obstacle.cactus_type == 1:
                self.small_pool.release(obstacle)
            else:
                self.big_pool.release(obstacle)
        elif isinstance(obstacle, Bird):
            self.bird_pool.release(obstacle)
    
    def update(self):
        if not self.model.is_running or not self.model.dino.is_alive:
            return
        
        self.model.dino.update()
        
        for obstacle in self.model.obstacles[:]:
            obstacle.update()
            
            # начисление очков
            if obstacle.x + obstacle.width <= self.model.dino.x + 10:
                if not obstacle.has_given_score:
                    obstacle.has_given_score = True
                    self.model.update_score(10)
                    print(f"[Score] +10! Всего: {self.model.score}")
            
            if obstacle.is_offscreen():
                self.model.obstacles.remove(obstacle)
                self._return_to_pool(obstacle)
                print(f"[Game] Препятствие удалено и возвращено в пул")
        
        self._check_collisions()
    
    def _check_collisions(self):
        resources = ResourceManager()
        
        dino_rect = pygame.Rect(self.model.dino.get_rect())
        if self.model.dino.state_machine.state == DinoState.RUNNING or self.model.dino.state_machine.state == DinoState.JUMPING:
            dino_texture = resources.dino_run_frames[0]
        elif self.model.dino.state_machine.state == DinoState.DUCKING:
            dino_texture = resources.dino_duck_frames[0]
        
        for obstacle in self.model.obstacles:
            obs_rect = pygame.Rect(obstacle.get_rect())
            
            if not dino_rect.colliderect(obs_rect):
                continue
            
            if hasattr(obstacle, 'cactus_type'):
                obs_texture = obstacle.cactus_picture
            else:
                obs_texture = resources.bird_frames[obstacle.current_frame]
            
            # Используем маски
            if mask_collision(dino_texture, obs_texture, dino_rect, obs_rect, resources):
                self.event_bus.emit(EVENT_COLLISION)
                self.model.dino.die()
                self.model.is_running = False
                break