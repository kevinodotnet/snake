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

### Terminal Echo Issue Fix
- **Problem**: Arrow keys printing "^[[A" to screen instead of being captured
- **Root Cause**: Terminal needs to be in raw mode BEFORE user presses keys, not after
- **Previous Approach**: Set raw mode only when reading input (too late)
- **New Approach**: Set raw mode for entire game session
  - Call setup_terminal() at start of run()
  - Keep terminal in raw mode throughout game
  - Call restore_terminal() in finally block
  - getch() no longer manages terminal mode, just reads from already-raw terminal
- **Expected Result**: Arrow keys should be captured as \x1b[A sequences, not echoed

## HTML Python Environment Bug Fixes

### ANSI Color Code Handling Bug (Fixed)
- **Problem**: ANSI reset codes (\033[0m) not properly closing HTML spans, causing color bleeding
- **Root Cause**: Simple regex replacement didn't track open tags or handle nested color codes
- **Fix**: Rewrote convertAnsiToHtml() function to properly track open span tags and close them on reset
- **Result**: Colors now reset properly without bleeding into subsequent text

### Emoji Spacing Inconsistency (Fixed) 
- **Problem**: Emoji rendering inconsistent between web and terminal versions
- **Fix**: Standardized emoji spacing in web version to match terminal behavior
- **Result**: Consistent grid layout between both versions

### Error Handling Missing (Fixed)
- **Problem**: No error handling for Pyodide loading failures or Python runtime errors
- **Fix**: Added comprehensive try-catch blocks for:
  - Pyodide initialization failures
  - Python code execution errors  
  - Game loop runtime errors
- **Result**: Better user experience with clear error messages instead of silent failures

### Grid Dimension Inconsistency (Fixed)
- **Problem**: Terminal version (80x40) vs web version (40x20) had different game areas
- **Fix**: Standardized web version to 80x40 and adjusted CSS for proper display
- **Result**: Consistent game experience across both platforms

### Regex Syntax Error (Fixed)
- **Problem**: Invalid regular expression syntax causing JavaScript error at runtime
- **Root Cause**: Incorrect escaping of backslashes in regex patterns for ANSI codes
- **Fix**: Changed from string-based regex construction to proper regex literals with correct escaping
- **Result**: JavaScript error eliminated, ANSI conversion now works properly

### Grid Layout Alignment Issue (Fixed)
- **Problem**: Snake head and food emojis misaligned with grid borders due to inconsistent spacing
- **Root Cause**: Mixed spacing - borders (██) had no extra space, emojis had +1 space, empty cells had +1 space
- **Fix**: Made spacing consistent - no extra space for double-width characters (borders and emojis), double space for empty cells
- **Result**: Perfect grid alignment with all elements properly positioned

### Snake Body Width Overflow Issue (Fixed)
- **Problem**: Snake body segments (emojis) causing grid to overflow on right side due to inconsistent character widths
- **Root Cause**: Emojis are inherently double-width Unicode characters with unpredictable rendering widths
- **Fix**: Replaced emojis with consistent ASCII characters:
  - Snake head: `●` (red bold)
  - Snake body: `○` (green)
  - Food: `*` (yellow bold)
  - All with consistent single-char + space padding to match double-width borders
- **Result**: Grid maintains perfect alignment regardless of snake length