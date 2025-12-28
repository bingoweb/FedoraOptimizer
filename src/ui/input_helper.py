import sys
import select
import tty
import termios
import contextlib

KEY_UP = 'KEY_UP'
KEY_DOWN = 'KEY_DOWN'
KEY_ENTER = 'KEY_ENTER'

class KeyListener:
    def __init__(self):
        self.old_settings = None

    def start(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    def stop(self):
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_key(self):
        # Non-blocking check
        if select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1)

            if ch == '\x1b':
                # Check for escape sequence (non-blocking immediate check)
                # Typically escape sequences arrive together
                if select.select([sys.stdin], [], [], 0.01)[0]:
                    seq = sys.stdin.read(2)
                    if seq == '[A': return KEY_UP
                    if seq == '[B': return KEY_DOWN
                return ch # Just ESC

            if ch == '\n' or ch == '\r':
                return KEY_ENTER

            return ch
        return None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
