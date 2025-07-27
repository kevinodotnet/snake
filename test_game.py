#!/usr/bin/env python3

from snake_game.game import SnakeGame

# Test with automated moves to verify rendering
test_moves = ['r', 'r', 'r', 'd', 'd', 'l', 'l', 'u', 'u']
game = SnakeGame(width=20, height=10, debug=True, moves=test_moves)
print("Testing with automated moves...")
game.run()