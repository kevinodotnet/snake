#!/usr/bin/env python3

import sys
import os
from .game import SnakeGame

def main():
    try:
        if os.name == 'nt':
            print("This game is optimized for Unix-like terminals.")
            print("For Windows, consider using WSL or a Unix-compatible terminal.")
            
        game = SnakeGame()
        game.run()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()