import pygame
import time
pygame.joystick.init()
pygame.display.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
joystick = joysticks[0]
joystick.init()
print("ONLY CONNECT ONE JOYSTICK AT A TIME!")
print("Found: ", joystick.get_name())
num_btn = joystick.get_numbuttons()
print("Number of Buttons: ", num_btn)
time.sleep(1)
try:
    while 1:
        pygame.event.pump()
        for i in range(num_btn):
            if joystick.get_button(i):
                print("Button: ", i, "triggered")
        time.sleep(0.1)
except:
    print("Ending poll loop")
    pygame.quit()
    quit()


# 0: Trigger
# 1: Middle Bottom on stick
# 2: Middle Top on stick
# 3: Left on Stick
# 4: Right on Stick
# 5: Left back on base
# 6: Left front on base
# 7: Middle left on base
# 8: Middle right on left
# 9: Right front on base
# 10: Right back on base


