from enum import Enum
import random
from config import C_percents

class DinoState(Enum):
    RUNNING = 1
    JUMPING = 2
    DUCKING = 3
    DEAD = 4


class StateMachine:
    
    def __init__(self, initial_state):
        self.state = initial_state
        self._transitions = {}
    
    def add_transition(self, from_state, to_state, condition=None):
        if from_state not in self._transitions:
            self._transitions[from_state] = []
        self._transitions[from_state].append((to_state, condition))
    
    def update(self):
        if self.state in self._transitions:
            for to_state, condition in self._transitions[self.state]:
                if condition is None or condition():
                    self.state = to_state
                    break
    
    def __repr__(self):
        transitions_str = []
        for from_state, rules in self._transitions.items():
            for to_state, condition in rules:
                cond_name = condition.__name__ if condition and hasattr(condition, '__name__') else str(condition)
                transitions_str.append(f"  {from_state.name} -> {to_state.name} [{cond_name}]")
        
        if transitions_str:
            transitions_block = "\n".join(transitions_str)
        else:
            transitions_block = "  (нет переходов)"
        
        return f"StateMachine(state={self.state.name},\n_transitions={{\n{transitions_block}\n}})"


class ObjectPool:
    
    def __init__(self, class_type, size, **default_args):
        self.class_type = class_type
        self.default_args = default_args
        self._pool = []
        self._active = []
        
        for i in range(size):
            obj = class_type(**default_args)
            obj.id = i
            self._pool.append(obj)
        
        print(f"[Pool] Создан пул для {class_type.__name__} размером {size}")
    
    def acquire(self, **override_args):
        if self._pool:
            idx = random.randint(0, len(self._pool) - 1)
            obj = self._pool.pop(idx)
            for key, value in override_args.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            self._active.append(obj)
            print(f"[Pool] {self.class_type.__name__} #{obj.id} ВЗЯТ, осталось: {len(self._pool)}")
            return obj
        else:
            print(f"[Pool] ОШИБКА! Пул {self.class_type.__name__} ПУСТ!")
            return None
    
    def release(self, obj):
        if obj in self._active:
            self._active.remove(obj)
            obj.reset()
            self._pool.append(obj)
            print(f"[Pool] {self.class_type.__name__} #{obj.id} ВОЗВРАЩЁН, в пуле: {len(self._pool)}")
    
    def release_all(self):
        for obj in self._active[:]:
            self.release(obj)


class ObstacleFactory:
    
    @staticmethod
    def create_small_cactus(x, y):
        from models import Cactus
        return Cactus(x, y, cactus_type=1)
    
    @staticmethod
    def create_big_cactus(x, y):
        from models import Cactus
        return Cactus(x, y, cactus_type=2)
    
    @staticmethod
    def create_bird(x, y):
        from models import Bird
        return Bird(x, y)
    
    @staticmethod
    def get_random_type(model):
        if model.nothing_prd.check():
            return None
        elif model.bird_prd.check():
            return 'bird'
        elif model.big_cactus_prd.check():
            return 'big_cactus'
        return 'small_cactus'


class PRD:

    def __init__(self,base_chance, name):
        self.base_chance = base_chance
        self.counter=0
        self.name = name
        self.C = C_percents[base_chance]

    def check(self):
        self.counter+=1
        current_chance = self.counter * self.C
        if random.random() < current_chance:
            self.reset()
            return True
        return False
    
    def reset(self):
        self.counter = 0

