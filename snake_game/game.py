import random
import time
import sys
import json
import termios
import tty
import select
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
        self.original_terminal_settings = None
        self.reset_game()
        self.state = GameState.PLAYING if (self.automated or self.skip_menu) else GameState.MENU
        
    def reset_game(self):
        self.snake: List[Tuple[int, int]] = [(self.width // 2, self.height // 2)]
        self.direction = Direction.RIGHT
        self.food: Optional[Tuple[int, int]] = None
        self.score = 0
        self.game_speed_ms = 150  # Milliseconds between moves
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
            if self.game_speed_ms > 50:
                self.game_speed_ms -= 5  # Get faster as score increases
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
            "game_speed_ms": self.game_speed_ms,
            "automated": self.automated,
            "skip_menu": self.skip_menu,
            "move_index": self.move_index,
            "total_moves": len(self.moves) if self.moves else 0,
            "moves_remaining": len(self.moves) - self.move_index if self.moves else 0
        }
        
    def print_debug_state(self):
        if self.debug:
            print(f"\nDEBUG STATE: {json.dumps(self.get_debug_state(), indent=2)}")
    
    def clear_screen(self):
        print('\033[2J\033[H', end='')
    
    def render_game(self):
        self.clear_screen()
        
        print(f"{Colors.YELLOW}{Colors.BOLD}🐍 SNAKE GAME 🐍{Colors.RESET}")
        print(f"Score: {Colors.GREEN}{self.score}{Colors.RESET} | Direction: {Colors.CYAN}{self.direction.name}{Colors.RESET}")
        print()
        
        # Create grid
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw borders
        for x in range(self.width):
            grid[0][x] = '█'
            grid[self.height - 1][x] = '█'
        for y in range(self.height):
            grid[y][0] = '█'
            grid[y][self.width - 1] = '█'
            
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                grid[y][x] = '●'  # Head
            else:
                grid[y][x] = '○'  # Body
                
        # Draw food
        if self.food:
            fx, fy = self.food
            grid[fy][fx] = '*'
            
        # Print grid
        for y in range(self.height):
            for x in range(self.width):
                char = grid[y][x]
                if char == '█':
                    print(f"{Colors.CYAN}{Colors.BOLD}{char}{Colors.RESET}", end='')
                elif char == '●':
                    print(f"{Colors.GREEN}{Colors.BOLD}{char}{Colors.RESET}", end='')
                elif char == '○':
                    print(f"{Colors.GREEN}{char}{Colors.RESET}", end='')
                elif char == '*':
                    print(f"{Colors.RED}{Colors.BOLD}{char}{Colors.RESET}", end='')
                else:
                    print(char, end='')
            print()
        
        print(f"\n{Colors.WHITE}Controls: Arrow keys or WASD to move, Q to quit{Colors.RESET}")
    
    def setup_terminal(self):
        """Set terminal to cbreak mode with no echo for the entire game session"""
        if not self.automated:
            try:
                fd = sys.stdin.fileno()
                self.original_terminal_settings = termios.tcgetattr(fd)
                # Use cbreak mode and disable echo
                new_attrs = termios.tcgetattr(fd)
                new_attrs[3] &= ~(termios.ICANON | termios.ECHO)  # Disable canonical mode and echo
                termios.tcsetattr(fd, termios.TCSADRAIN, new_attrs)
            except Exception as e:
                print(f"Warning: Could not set terminal mode: {e}")
    
    def restore_terminal(self):
        """Restore terminal to original settings"""
        if self.original_terminal_settings and not self.automated:
            try:
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, self.original_terminal_settings)
            except Exception as e:
                print(f"Warning: Could not restore terminal: {e}")

    def getch(self, timeout_ms: int = None):
        """Get a single character from stdin with optional timeout
        Terminal should already be in cbreak mode when this is called.
        
        Args:
            timeout_ms: Timeout in milliseconds. If None, blocks indefinitely.
            
        Returns:
            str: Character pressed, or None if timeout occurred
        """
        if timeout_ms is not None:
            # Use select to wait for input with timeout
            timeout_sec = timeout_ms / 1000.0
            ready, _, _ = select.select([sys.stdin], [], [], timeout_sec)
            
            if not ready:
                # Timeout occurred, no input available
                return None
        
        # Input is available (or no timeout specified)
        # Terminal is already in cbreak mode, just read
        ch = sys.stdin.read(1)
        
        # Handle arrow keys
        if ch == '\x1b':
            # For arrow keys, we need to read the next 2 characters
            # Use a short timeout to avoid hanging if it's just ESC
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                ch += sys.stdin.read(2)
                
        return ch
    
    def handle_input(self, key: str) -> bool:
        """Handle keyboard input. Returns False if should quit"""
        print(f"key:{key}")
        if key.lower() == 'q':
            return False
        else:
            # TEMPORARY DEBUG: Make ANY key change direction to UP
            print(f"DEBUG: Changing direction to UP for any key: {repr(key)}")
            self.change_direction(Direction.UP)
        return True
            
    def run(self):
        # Set up terminal for raw mode
        self.setup_terminal()
        
        try:
            if self.automated or self.skip_menu:
                self.state = GameState.PLAYING
                
            while True:
                if self.automated and self.is_moves_exhausted():
                    break
                    
                if self.state == GameState.PLAYING:
                    # Render the game (unless automated and not debug)
                    if not self.automated or self.debug:
                        self.render_game()
                        
                    if self.debug:
                        self.print_debug_state()
                        
                    # Handle input BEFORE moving the snake
                    if self.automated:
                        next_move = self.get_next_move()
                        if next_move:
                            self.process_automated_move(next_move)
                    else:
                        # Interactive mode - get keyboard input with timeout
                        try:
                            key = self.getch(timeout_ms=self.game_speed_ms)
                            if key and not self.handle_input(key):
                                break  # User pressed Q to quit
                        except KeyboardInterrupt:
                            break
                    
                    if not self.move_snake():
                        self.state = GameState.GAME_OVER
                        # Show game over screen
                        self.render_game()
                        print(f"\n{Colors.RED}{Colors.BOLD}GAME OVER!{Colors.RESET}")
                        print(f"Final Score: {Colors.YELLOW}{self.score}{Colors.RESET}")
                        if not self.automated:
                            print("Press any key to exit...")
                            self.getch()
                        break
                        
                    # For automated mode, still add a small delay
                    if self.automated and not self.debug:
                        time.sleep(0.1)
                            
        except KeyboardInterrupt:
            pass
        finally:
            # Restore terminal settings
            self.restore_terminal()
            if self.automated:
                print(f"\nFINAL STATE: {json.dumps(self.get_debug_state(), indent=2)}")
            print(f"\n{Colors.YELLOW}Thanks for playing Snake! 🐍{Colors.RESET}")