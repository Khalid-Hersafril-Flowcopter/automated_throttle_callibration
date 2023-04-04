import os
import sys

# Hacky way to get import working
path = os.path.join(os.path.dirname(__file__), '..', 'lcd_setup')
sys.path.insert(1, path)
print(path)

import special_char

print(special_char.Unlocked)
