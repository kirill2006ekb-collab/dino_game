import pygame
import os
from config import *
from patterns import DinoState
import random
from models import *

class ResourceManager:
    """Менеджер ресурсов (Singleton) — загружает текстуры один раз"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_resources()
            cls._instance._mask_cache = {}          # кэш масок
        return cls._instance
    
    def _load_resources(self):
        assets_dir = "assets"
        
        self.ground_texture = pygame.image.load(f"{assets_dir}/Ground.png")
        self.ground_texture = pygame.transform.scale(self.ground_texture, (SCREEN_WIDTH, 14))

        # Загружаем кадры анимации
        self.dino_run_frames = []
        self.dino_run_frames.append(pygame.image.load(f"{assets_dir}/dino_run1.png"))
        self.dino_run_frames.append(pygame.image.load(f"{assets_dir}/dino_run2.png"))

        self.dino_duck_frames = []
        self.dino_duck_frames.append(pygame.image.load(f"{assets_dir}/dino_duck1.png"))
        self.dino_duck_frames.append(pygame.image.load(f"{assets_dir}/dino_duck2.png"))
        
        self.bird_frames = []
        self.bird_frames.append(pygame.image.load(f"{assets_dir}/bird_up.png"))
        self.bird_frames.append(pygame.image.load(f"{assets_dir}/bird_down.png"))

        self.flockbird_frames = []
        self.flockbird_frames.append(pygame.image.load(f"{assets_dir}/flockbird_up.png"))
        self.flockbird_frames.append(pygame.image.load(f"{assets_dir}/flockbird_down.png"))

        # Преобразуем размеры под игру
        for i in range(2):
            self.dino_run_frames[i] = pygame.transform.scale(self.dino_run_frames[i], (dino_width, dino_height))
        
        for i in range(2):
            self.dino_duck_frames[i] = pygame.transform.scale(self.dino_duck_frames[i], (dino_width+10, dino_height//1.5))
        
        for i in range(2):
            self.bird_frames[i] = pygame.transform.scale(self.bird_frames[i], (bird_width, bird_height))

        for i in range(2):
            self.flockbird_frames[i] = pygame.transform.scale(self.flockbird_frames[i], (flockbird_width, flockbird_height))

        self.cactus = []
        for i in range(1, 5):
            self.cactus.append(pygame.image.load(f"{assets_dir}/Cactus-{i}.png"))

    def get_mask(self, surface):
        if surface not in self._mask_cache:
            self._mask_cache[surface] = pygame.mask.from_surface(surface)
        return self._mask_cache[surface]


class DinoView:
    
    def __init__(self,event_bus):
        self.event_bus = event_bus
        self.resources = ResourceManager()
        self.animation_timer = 0
    
    def draw(self, screen, dino_model):
        x, y, w, h = dino_model.get_rect()
        
        if not dino_model.is_alive:
            return
        
        if dino_model.state_machine.state == DinoState.RUNNING:
            self.animation_timer += 1
            frame_index = (self.animation_timer // 10) % 2
            if self.animation_timer % 10 == 0:
                self.event_bus.emit(STEP)
            texture = self.resources.dino_run_frames[frame_index]
            screen.blit(texture, (x, y))
        
        elif dino_model.state_machine.state == DinoState.DUCKING:
            self.animation_timer += 1
            frame_index = (self.animation_timer // 10) % 2
            if self.animation_timer % 10 == 0:
                self.event_bus.emit(STEP)
            texture = self.resources.dino_duck_frames[frame_index]
            screen.blit(texture, (x, y))
        
        else:
            # Прыжок — используем первый кадр бега
            screen.blit(self.resources.dino_run_frames[0], (x, y))


class ObstacleView:
    
    def __init__(self,event_bus):
        self.resources = ResourceManager()
        self.event_bus = event_bus
    
    def draw(self, screen, obstacle):
        x, y, w, h = obstacle.get_rect()
        
        if isinstance(obstacle, Cactus):
            if obstacle.cactus_picture is None:
                obstacle.cactus_picture = pygame.transform.scale(random.choice(self.resources.cactus), (w, h))
            screen.blit(obstacle.cactus_picture, (x, y))
        elif isinstance(obstacle, Bird):
            texture = self.resources.bird_frames[obstacle.current_frame]
            screen.blit(texture, (x, y))
        elif isinstance(obstacle, FlockBird):
            texture = self.resources.flockbird_frames[obstacle.current_frame]
            screen.blit(texture, (x, y))


class GameView:
    
    def __init__(self, screen,event_bus):
        self.event_bus = event_bus
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)
        self.dino_view = DinoView(self.event_bus)
        self.obstacle_view = ObstacleView(self.event_bus)
        self.resources = ResourceManager()
    
    def render(self, game_model):
        self.screen.fill(COLORS['WHITE'])
        
        if self.resources.ground_texture:
            ground_width = self.resources.ground_texture.get_width()
            
            offset = int(game_model.ground_offset % ground_width)
            
            self.screen.blit(self.resources.ground_texture, (-offset, GROUND_Y-11))
            self.screen.blit(self.resources.ground_texture, (ground_width - offset, GROUND_Y-11))
        else:
            pygame.draw.line(self.screen, COLORS['BLACK'], 
                            (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
        
        self.dino_view.draw(self.screen, game_model.dino)
        
        for obstacle in game_model.obstacles:
            self.obstacle_view.draw(self.screen, obstacle)
        
        score_text = self.font.render(f"Score: {game_model.score}", True, COLORS['BLACK'])
        self.screen.blit(score_text, (10, 10))
        
        speed_text = self.small_font.render(
            f"Speed: {game_model.game_speed:.1f}", 
            True, COLORS['BLACK']
        )
        self.screen.blit(speed_text, (10, 50))
        
        if not game_model.is_running or not game_model.dino.is_alive:
            game_over_text = self.font.render("GAME OVER - Press R", True, COLORS['RED'])
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()


def mask_collision(sprite1, sprite2, rect1, rect2, resources):
    """Проверяет пересечение непрозрачных пикселей двух спрайтов через маски."""
    overlap_rect = rect1.clip(rect2)
    if overlap_rect.width <= 0 or overlap_rect.height <= 0:
        return False

    mask1 = resources.get_mask(sprite1)
    mask2 = resources.get_mask(sprite2)

    offset = (rect2.x - rect1.x, rect2.y - rect1.y)
    return mask1.overlap(mask2, offset) is not None