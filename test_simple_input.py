#!/usr/bin/env python3

import sys
import os
import fcntl
import errno

print("Testing simple non-blocking input...")
print("Try typing some keys (they might not show up immediately)")
print("Type 'q' to quit")

try:
    # Make stdin non-blocking
    fd = sys.stdin.fileno()
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    print("Set non-blocking mode successfully")
    
    while True:
        try:
            key = os.read(fd, 1).decode('utf-8', errors='ignore')
            if key:
                print(f"Got key: {repr(key)}")
                if key.lower() == 'q':
                    break
        except OSError as e:
            if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                # No input available, continue
                pass
            else:
                print(f"Read error: {e}")
                break

except Exception as e:
    print(f"Error: {e}")

print("Done")