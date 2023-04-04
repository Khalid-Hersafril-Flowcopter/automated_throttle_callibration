from RPLCD import *
from time import sleep
from RPLCD.i2c import CharLCD
from special_char import Locked

lcd = CharLCD('PCF8574', 0x27)

print(Locked)
i = 0
lcd.create_char(0, Locked)
lcd.write_string('Hello there, \x00')

#while i < 10:
#    lcd.cursor_pos = (0, 0)
#    lcd.write_string(Locked)
#    i += 1
#    sleep(1)
