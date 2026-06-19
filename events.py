from typing import Dict, List, Callable, Any

class EventBus:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.listeners = {}
        return cls._instance
    
    def subscribe(self, event: str, callback: Callable):
        self.listeners.setdefault(event, []).append(callback)
    
    def emit(self, event: str, data: Any = None):
        for callback in self.listeners.get(event, []):
            callback(data)
    
    def clear(self):
        self.listeners.clear()