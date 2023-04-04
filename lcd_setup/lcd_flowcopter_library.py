from RPLCD import *
from time import sleep
from RPLCD.i2c import CharLCD
lcd = CharLCD('PCF8574', 0x27)

i = 0

while i < 10:
    lcd.cursor_pos = (0, 0)
    lcd.write_string(str(i))
    i += 1
    sleep(1)
