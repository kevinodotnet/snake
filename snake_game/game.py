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
            
        
    def get_key(self, timeout=0):
        """Simple keyboard input that works in most environments"""
        try:
            # For non-blocking input, try a simple approach
            if timeout == 0:
                # Try to check if there's any input using a very short timeout
                import select
                ready = select.select([sys.stdin], [], [], 0.001)  # 1ms timeout
                if not ready[0]:
                    return None
            
            # If we get here, there might be input available
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                
                if not key:  # Empty string means EOF or closed stdin
                    self.log_debug("get_key() got empty string (EOF)")
                    return None
                    
                self.log_debug(f"get_key() read character: {repr(key)}")
                
                # Handle arrow keys
                if key == '\x1b':
                    try:
                        key += sys.stdin.read(2)
                        self.log_debug(f"Arrow key sequence: {repr(key)}")
                    except:
                        pass
                
                return key
                
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
        except Exception as e:
            self.log_debug(f"get_key() exception: {e}")
            return None
        
    def handle_input(self, key: str):
        self.last_key = key
        
        # Debug logging and breakpoint when key is pressed
        if key and not self.automated:
            self.log_debug(f"handle_input() called with key: {repr(key)}")
            # breakpoint()
        
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
        
    def log_debug(self, message: str):
        """Add a debug message to the display queue"""
        if not self.automated:  # Only log for interactive games
            import time
            timestamp = time.strftime("%H:%M:%S")
            self.debug_messages.append(f"[{timestamp}] {message}")
            # Keep only last 10 messages
            if len(self.debug_messages) > 10:
                self.debug_messages.pop(0)
                
    def setup_terminal(self):
        """Set up terminal for raw input mode"""
        if not self.automated:
            try:
                import fcntl
                fd = sys.stdin.fileno()
                # Only try to save settings if we can get them
                try:
                    self.original_terminal_settings = termios.tcgetattr(fd)
                    tty.setraw(fd)
                    self.log_debug("Terminal set to raw mode")
                except OSError:
                    # Fallback for environments that don't support raw mode
                    self.log_debug("Raw mode not available, using fallback")
                    pass
                
                # Make stdin non-blocking (this usually works even when raw mode doesn't)
                flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                self.log_debug("Set non-blocking mode")
            except Exception as e:
                self.log_debug(f"Failed to setup terminal: {e}")
                
    def restore_terminal(self):
        """Restore terminal to original settings"""
        if self.original_terminal_settings and not self.automated:
            try:
                import fcntl
                fd = sys.stdin.fileno()
                # Restore blocking mode
                flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
                # Restore original settings
                termios.tcsetattr(fd, termios.TCSADRAIN, self.original_terminal_settings)
                self.log_debug("Terminal restored")
            except Exception as e:
                self.log_debug(f"Failed to restore terminal: {e}")
        
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
            "skip_menu": self.skip_menu,
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
            key = self.get_key(timeout=1)
            return key
        return None
        
    def run(self):
        # Set up terminal for raw input
        self.setup_terminal()
        
        try:
            if self.automated or self.skip_menu:
                self.state = GameState.PLAYING
                
            while True:
                if self.automated and self.is_moves_exhausted():
                    break
                    
                if self.state == GameState.MENU:
                    if not self.automated:
                        self.render_menu()
                        if self.debug:
                            self.print_debug_state()
                        key = self.get_key(timeout=1)
                        if key and not self.handle_input(key):
                            break
                    else:
                        self.state = GameState.PLAYING
                        
                elif self.state == GameState.PLAYING:
                    if not self.automated or self.debug:
                        self.render_game()
                        
                    if self.debug:
                        self.print_debug_state()
                        
                    # Handle input BEFORE moving the snake
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
                        else:
                            # Non-debug mode: Try different input methods
                            try:
                                # First try direct read
                                key = os.read(sys.stdin.fileno(), 1).decode('utf-8', errors='ignore')
                                if key:
                                    self.log_debug(f"Read key: {repr(key)}")
                                    
                                    if key == '\x1b':
                                        # Read arrow key sequence
                                        try:
                                            additional = os.read(sys.stdin.fileno(), 2).decode('utf-8', errors='ignore')
                                            key += additional
                                            self.log_debug(f"Arrow key: {repr(key)}")
                                        except:
                                            pass
                                    
                                    if not self.handle_input(key):
                                        break
                                        
                            except OSError as e:
                                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                                    self.log_debug(f"Read error: {e}")
                                # If direct read fails, try the original get_key approach
                                try:
                                    key = self.get_key(timeout=0)
                                    if key and not self.handle_input(key):
                                        break
                                except:
                                    pass
                    
                    if not self.move_snake():
                        self.state = GameState.GAME_OVER
                        continue
                        
                    if not self.debug and not self.automated:
                        time.sleep(self.game_speed)
                    elif self.automated and not self.debug:
                        time.sleep(0.1)
                            
                elif self.state == GameState.GAME_OVER:
                    # Render final game state and exit
                    self.render_game()
                    print(f"\n{Colors.RED}{Colors.BOLD}GAME OVER!{Colors.RESET}")
                    print(f"{Colors.WHITE}Final Score: {Colors.YELLOW}{self.score}{Colors.RESET}")
                    if self.automated:
                        print(f"\nFINAL STATE: {json.dumps(self.get_debug_state(), indent=2)}")
                    break
                        
        except KeyboardInterrupt:
            # For Ctrl+C, show final game state
            self.render_game()
            print(f"\n{Colors.RED}{Colors.BOLD}GAME INTERRUPTED!{Colors.RESET}")
            print(f"{Colors.WHITE}Final Score: {Colors.YELLOW}{self.score}{Colors.RESET}")
        finally:
            # Restore terminal settings
            self.restore_terminal()
            # Don't clear screen on exit - leave final state visible
            if self.automated and not self.state == GameState.GAME_OVER:
                print(f"\nFINAL STATE: {json.dumps(self.get_debug_state(), indent=2)}")
            print(f"\n{Colors.YELLOW}Thanks for playing Snake! 🐍{Colors.RESET}")