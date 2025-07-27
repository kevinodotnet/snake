# Snake Game Development Notes

## Implementation History

### Initial Complex Implementation (Removed)
- Started with complex terminal handling using termios, tty, select, fcntl
- Had extensive rendering code with debug messages, multiple game states
- Input handling was overly complicated with non-blocking I/O
- User reported keyboard input completely broken - keys not detected
- Decided to start over with simpler approach

### Clean Restart - Core Game Logic Only
- Removed ALL rendering and input/TTY handling code
- Kept only core game mechanics:
  - Snake movement and collision detection
  - Food placement and scoring
  - Direction changes and game state
  - Automated moves functionality (working perfectly)
- Verified core logic works with automated testing

### Simple Rendering + Basic Input (Working)
- Added simple screen clearing with ANSI escape codes
- Basic colored grid rendering: snake head (●), body (○), food (*), borders (█)
- Simple getch() function using termios.tcgetattr/tcsetattr and tty.setraw
- Added keyboard input handling for arrow keys (\x1b[A/B/C/D) and WASD
- Game responds to keys but blocks waiting for input (no automatic advancement)

### Timeout-Based Input (Fixed Input Detection Issue)
- **Problem**: Game needed to advance automatically even without input
- **Solution**: Added timeout-based input using select.select()
- Changed game speed from seconds to milliseconds (game_speed_ms = 150ms)
- Game waits up to 150ms for input, then advances snake automatically
- Speed increases as score increases (gets 5ms faster per food, minimum 50ms)

### Input Detection Fix
- **Problem**: After adding timeout, keyboard input stopped being detected
- **Root Cause**: Was setting raw mode before checking if input was available
- **Fix**: Moved select.select() call outside terminal setup
- Now checks input availability first, only sets raw mode when input exists
- **Current Status**: Game advances automatically AND detects keyboard input properly

## Current Features Working
- ✅ Automatic snake advancement with configurable timing (150ms default)
- ✅ Arrow keys and WASD controls detected properly  
- ✅ Colored terminal display with borders, snake, and food
- ✅ Score tracking and speed increases
- ✅ Game over detection and display
- ✅ Both automated mode (for testing) and interactive mode
- ✅ Clean quit with 'Q' key

## Technical Approach
- Uses select.select() for timeout-based input waiting
- Simple termios/tty raw mode only when input is available
- Single-character reading with arrow key sequence detection
- ANSI color codes for terminal display
- Grid-based rendering system