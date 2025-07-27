#!/usr/bin/env python3

import sys
import os
import argparse
from .game import SnakeGame

def main():
    parser = argparse.ArgumentParser(description='Terminal Snake Game')
    parser.add_argument('-d', '--debug', action='store_true', 
                       help='Enable debug mode with JSON state dumps')
    parser.add_argument('--width', type=int, default=40, 
                       help='Game width (default: 40)')
    parser.add_argument('--height', type=int, default=20, 
                       help='Game height (default: 20)')
    parser.add_argument('--moves', type=str, 
                       help='Sequence of moves: u(up), d(down), l(left), r(right), .(no move)')
    
    args = parser.parse_args()
    
    try:
        if os.name == 'nt':
            print("This game is optimized for Unix-like terminals.")
            print("For Windows, consider using WSL or a Unix-compatible terminal.")
            
        moves = list(args.moves) if args.moves else None
        game = SnakeGame(width=args.width, height=args.height, debug=args.debug, moves=moves)
        game.run()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()