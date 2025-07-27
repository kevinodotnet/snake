#!/usr/bin/env python3

import sys
import termios
import tty

def get_key():
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
                
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

print("Press arrow keys, numpad keys, or 'q' to quit:")
while True:
    key = get_key()
    print(f"Key pressed: {repr(key)}")
    if key.lower() == 'q':
        break