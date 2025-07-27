#!/usr/bin/env python3

import sys
from snake_game.game import SnakeGame

def test_input():
    """Test that keyboard input works without echo"""
    print("Testing keyboard input (without terminal mode changes)...")
    
    game = SnakeGame(width=15, height=8, skip_menu=True)
    
    # Test the getch function directly
    print("Press any key (will not echo to screen):")
    try:
        key = game.getch(timeout_ms=5000)  # 5 second timeout
        if key:
            print(f"Key detected: {repr(key)}")
            if key == '\x1b[A':
                print("✅ Up arrow detected correctly")
            elif key == '\x1b[B':
                print("✅ Down arrow detected correctly") 
            elif key == '\x1b[C':
                print("✅ Right arrow detected correctly")
            elif key == '\x1b[D':
                print("✅ Left arrow detected correctly")
            else:
                print(f"✅ Key '{key}' detected correctly")
        else:
            print("❌ No key detected within timeout")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_input()