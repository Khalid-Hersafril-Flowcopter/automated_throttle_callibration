import os
import sys

path = os.path.join(os.getcwd(), '..', 'lcd_setup')
sys.path.insert(1, path)

import special_char

special_char.test()
