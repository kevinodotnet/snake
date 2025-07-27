import random
import time
import sys
import termios
import tty
import select
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
    def __init__(self, width: int = 40, height: int = 20, debug: bool = False, moves: List[str] = None):
        self.width = width
        self.height = height
        self.debug = debug
        self.moves = moves or []
        self.move_index = 0
        self.automated = bool(moves)
        self.reset_game()
        self.state = GameState.MENU
        self.last_key = None
        
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
            
    def clear_screen(self):
        print('\033[2J\033[H', end='')
        
    def render_border(self):
        border_char = '█'
        print(f"{Colors.CYAN}{Colors.BOLD}", end='')
        
        print(border_char * self.width)
        
        for y in range(1, self.height - 1):
            print(border_char, end='')
            print(' ' * (self.width - 2), end='')
            print(border_char)
            
        print(border_char * self.width)
        print(Colors.RESET, end='')
        
    def render_game(self):
        self.clear_screen()
        
        print(f"{Colors.YELLOW}{Colors.BOLD}🐍 SNAKE GAME 🐍{Colors.RESET}")
        print(f"{Colors.WHITE}Score: {Colors.GREEN}{self.score}{Colors.RESET}")
        print()
        
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        for x in range(self.width):
            grid[0][x] = '█'
            grid[self.height - 1][x] = '█'
        for y in range(self.height):
            grid[y][0] = '█'
            grid[y][self.width - 1] = '█'
            
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                grid[y][x] = '●'
            else:
                grid[y][x] = '○'
                
        if self.food:
            fx, fy = self.food
            grid[fy][fx] = '🍎'
            
        for y in range(self.height):
            for x in range(self.width):
                char = grid[y][x]
                if char == '█':
                    print(f"{Colors.CYAN}{Colors.BOLD}{char}{Colors.RESET}", end='')
                elif char == '●':
                    print(f"{Colors.GREEN}{Colors.BOLD}{char}{Colors.RESET}", end='')
                elif char == '○':
                    print(f"{Colors.GREEN}{char}{Colors.RESET}", end='')
                elif char == '🍎':
                    print(f"{Colors.RED}{Colors.BOLD}{char}{Colors.RESET}", end='')
                else:
                    print(char, end='')
            print()
            
    def render_menu(self):
        self.clear_screen()
        print(f"{Colors.YELLOW}{Colors.BOLD}")
        print("🐍" * 20)
        print("      SNAKE GAME")
        print("🐍" * 20)
        print(f"{Colors.RESET}")
        print()
        print(f"{Colors.WHITE}Controls:{Colors.RESET}")
        print(f"{Colors.GREEN}Arrow Keys{Colors.RESET} or {Colors.GREEN}Numpad 4/5/6/8{Colors.RESET} - Move")
        print(f"{Colors.GREEN}Q{Colors.RESET} - Quit")
        print(f"{Colors.GREEN}R{Colors.RESET} - Restart (when game over)")
        print()
        print(f"{Colors.CYAN}Press any key to start!{Colors.RESET}")
        
    def render_game_over(self):
        self.clear_screen()
        print(f"{Colors.RED}{Colors.BOLD}")
        print("💀" * 15)
        print("   GAME OVER!")
        print("💀" * 15)
        print(f"{Colors.RESET}")
        print()
        print(f"{Colors.WHITE}Final Score: {Colors.YELLOW}{self.score}{Colors.RESET}")
        print()
        print(f"{Colors.GREEN}R{Colors.RESET} - Play Again")
        print(f"{Colors.GREEN}Q{Colors.RESET} - Quit")
        
    def get_key(self):
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                
                if key == '\x1b':
                    try:
                        key += sys.stdin.read(2)
                    except:
                        pass
                elif key in '4568':
                    return key
                    
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return key
        except:
            return 'q'
        
    def handle_input(self, key: str):
        self.last_key = key
        
        if self.state == GameState.MENU:
            if key.lower() == 'q':
                return False
            else:
                self.state = GameState.PLAYING
                return True
                
        elif self.state == GameState.PLAYING:
            if key.lower() == 'q':
                return False
            elif key == '\x1b[A' or key == '8':
                self.change_direction(Direction.UP)
            elif key == '\x1b[B' or key == '5':
                self.change_direction(Direction.DOWN)
            elif key == '\x1b[D' or key == '4':
                self.change_direction(Direction.LEFT)
            elif key == '\x1b[C' or key == '6':
                self.change_direction(Direction.RIGHT)
                
        elif self.state == GameState.GAME_OVER:
            if key.lower() == 'q':
                return False
            elif key.lower() == 'r':
                self.reset_game()
                self.state = GameState.PLAYING
                
        return True
        
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
            "last_key": self.last_key,
            "game_speed": self.game_speed,
            "automated": self.automated,
            "move_index": self.move_index,
            "total_moves": len(self.moves) if self.moves else 0,
            "moves_remaining": len(self.moves) - self.move_index if self.moves else 0
        }
        
    def print_debug_state(self):
        if self.debug:
            print(f"\nDEBUG STATE: {json.dumps(self.get_debug_state(), indent=2)}")
            
    def wait_for_debug_input(self):
        if self.debug:
            print("DEBUG: Press arrow key to move, ENTER to continue, or 'q' to quit...")
            key = self.get_key()
            return key
        return None
        
    def run(self):
        try:
            if self.automated:
                self.state = GameState.PLAYING
                
            while True:
                if self.automated and self.is_moves_exhausted():
                    break
                    
                if self.state == GameState.MENU:
                    if not self.automated:
                        self.render_menu()
                        if self.debug:
                            self.print_debug_state()
                        key = self.get_key()
                        if not self.handle_input(key):
                            break
                    else:
                        self.state = GameState.PLAYING
                        
                elif self.state == GameState.PLAYING:
                    if not self.automated or self.debug:
                        self.render_game()
                        
                    if self.debug:
                        self.print_debug_state()
                        
                    if self.automated:
                        next_move = self.get_next_move()
                        if next_move:
                            self.process_automated_move(next_move)
                        if self.debug and not self.is_moves_exhausted():
                            debug_key = self.wait_for_debug_input()
                            if debug_key and debug_key.lower() == 'q':
                                break
                    else:
                        if self.debug:
                            debug_key = self.wait_for_debug_input()
                            if debug_key and debug_key.lower() == 'q':
                                break
                            if debug_key and debug_key != '\n' and debug_key != '\r':
                                self.handle_input(debug_key)
                    
                    if not self.move_snake():
                        self.state = GameState.GAME_OVER
                        continue
                        
                    if not self.debug and not self.automated:
                        time.sleep(self.game_speed)
                        
                        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                            key = self.get_key()
                            if not self.handle_input(key):
                                break
                    elif self.automated and not self.debug:
                        time.sleep(0.1)
                            
                elif self.state == GameState.GAME_OVER:
                    if not self.automated:
                        self.render_game_over()
                        if self.debug:
                            self.print_debug_state()
                        key = self.get_key()
                        if not self.handle_input(key):
                            break
                    else:
                        break
                        
        except KeyboardInterrupt:
            pass
        finally:
            if self.automated:
                print(f"\nFINAL STATE: {json.dumps(self.get_debug_state(), indent=2)}")
            self.clear_screen()
            print(f"{Colors.YELLOW}Thanks for playing Snake! 🐍{Colors.RESET}")