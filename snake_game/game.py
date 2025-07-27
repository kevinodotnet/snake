import random
import time
import sys
import json
from typing import List, Tuple, Optional
from enum import Enum

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    BG_BLACK = '\033[40m'
    BG_GREEN = '\033[42m'
    BG_RED = '\033[41m'

class SnakeGame:
    def __init__(self, width: int = 40, height: int = 20, debug: bool = False, moves: List[str] = None, skip_menu: bool = False):
        self.width = width
        self.height = height
        self.debug = debug
        self.moves = moves or []
        self.move_index = 0
        self.automated = bool(moves)
        self.skip_menu = skip_menu
        self.reset_game()
        self.state = GameState.PLAYING if (self.automated or self.skip_menu) else GameState.MENU
        
    def reset_game(self):
        self.snake: List[Tuple[int, int]] = [(self.width // 2, self.height // 2)]
        self.direction = Direction.RIGHT
        self.food: Optional[Tuple[int, int]] = None
        self.score = 0
        self.game_speed = 0.15
        self.place_food()
        
    def place_food(self):
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
                
    def move_snake(self) -> bool:
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        if (new_head[0] <= 0 or new_head[0] >= self.width - 1 or
            new_head[1] <= 0 or new_head[1] >= self.height - 1 or
            new_head in self.snake):
            return False
            
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.score += 10
            self.place_food()
            if self.game_speed > 0.05:
                self.game_speed -= 0.005
        else:
            self.snake.pop()
            
        return True
        
    def change_direction(self, new_direction: Direction):
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        if new_direction != opposite_directions.get(self.direction):
            self.direction = new_direction
            
    def get_next_move(self) -> Optional[str]:
        if not self.automated or self.move_index >= len(self.moves):
            return None
        
        move = self.moves[self.move_index]
        self.move_index += 1
        return move
        
    def process_automated_move(self, move: str):
        if move == 'u' or move == '8':
            self.change_direction(Direction.UP)
        elif move == 'd' or move == '5':
            self.change_direction(Direction.DOWN)
        elif move == 'l' or move == '4':
            self.change_direction(Direction.LEFT)
        elif move == 'r' or move == '6':
            self.change_direction(Direction.RIGHT)
        elif move == '.':
            pass
        
    def is_moves_exhausted(self) -> bool:
        return self.automated and self.move_index >= len(self.moves)
        
    def get_debug_state(self) -> dict:
        return {
            "state": self.state.value,
            "snake_head": self.snake[0] if self.snake else None,
            "snake_length": len(self.snake),
            "direction": self.direction.name,
            "food_position": self.food,
            "score": self.score,
            "game_speed": self.game_speed,
            "automated": self.automated,
            "skip_menu": self.skip_menu,
            "move_index": self.move_index,
            "total_moves": len(self.moves) if self.moves else 0,
            "moves_remaining": len(self.moves) - self.move_index if self.moves else 0
        }
        
    def print_debug_state(self):
        if self.debug:
            print(f"\nDEBUG STATE: {json.dumps(self.get_debug_state(), indent=2)}")
            
    def run(self):
        try:
            if self.automated or self.skip_menu:
                self.state = GameState.PLAYING
                
            while True:
                if self.automated and self.is_moves_exhausted():
                    break
                    
                if self.state == GameState.PLAYING:
                    if self.debug:
                        self.print_debug_state()
                        
                    # Handle input BEFORE moving the snake
                    if self.automated:
                        next_move = self.get_next_move()
                        if next_move:
                            self.process_automated_move(next_move)
                    
                    if not self.move_snake():
                        self.state = GameState.GAME_OVER
                        continue
                        
                    if not self.debug and not self.automated:
                        time.sleep(self.game_speed)
                    elif self.automated and not self.debug:
                        time.sleep(0.1)
                            
                elif self.state == GameState.GAME_OVER:
                    break
                        
        except KeyboardInterrupt:
            pass
        finally:
            if self.automated:
                print(f"\nFINAL STATE: {json.dumps(self.get_debug_state(), indent=2)}")