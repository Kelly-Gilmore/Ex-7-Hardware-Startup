import os
import spidev
import time
import threading

from time import sleep

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.stepper import stepper
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

from Slush.Devices import L6470Registers
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus

import RPi.GPIO as GPIO

spi = spidev.SpiDev()

s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
                 steps_per_unit=200, speed=8)

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """


    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    motor = ObjectProperty()
    pos_1 = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.motor = False
        self.direction = 0



    def run_motor(self):
        self.motor = not self.motor
        if self.motor:
            s0.run(0, 20)
        else:
            s0.softStop()

    def change_direction(self):
        self.direction = not self.direction
        if self.direction:
            self.direction = self.direction + 1
            s0.run(1, 20)
        else:
            s0.run(0, 20)

    def adjust_speed(self):
        s0.run(self.direction, int(self.ids.sheep.value))

    def big_function(self):
        s0.set_speed(1)
        s0.relative_move(15)
        time.sleep(10)
        s0.set_speed(5)
        s0.relative_move(10)
        time.sleep(8)
        s0.goHome()
        time.sleep(30)
        s0.set_speed(8)
        s0.relative_move(-100)
        time.sleep(10)
        s0.goHome()

    def binary_state(self):
        cyprus.initialize()
        cyprus.setup_servo(1)
        cyprus.set_servo_position(1, 0)
        sleep(1)
        cyprus.set_servo_position(1, 1)

    def limit_switch(self):
        cyprus.initialize()
        cyprus.setup_servo(1)
        def isGPIO_P6_HIGH(self):
            return (cyprus.read_gpio() & 0b0001) == 1
        if isGPIO_P6_HIGH(self):
            cyprus.set_servo_position(1, 0)
        else:
            cyprus.set_servo_position(1, 1)

    def talon_switch(self):
        cyprus.initialize()
        cyprus.setup_servo(1)
        def isGPIO_P6_HIGH(self):
            return (cyprus.read_gpio() & 0b0001) == 1
        if isGPIO_P6_HIGH(self):
            cyprus.set_servo_speed(1, 0)
        else:
            cyprus.set_servo_speed(1, 1)

    def cytron_dc(self):
        cyprus.initialize()
        cyprus.set_pwm_values(2, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        sleep(.5)
        cyprus.set_pwm_values(2, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        sleep(5)
        cyprus.set_pwm_values(2, period_value=100000, compare_value=-100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        sleep(.5)
        cyprus.set_pwm_values(2, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        cyprus.close()

    def thread_prox_sensor(self):
        y = threading.Thread(target=self.prox_sensor, daemon=True)
        y.start()


    def prox_sensor(self):
        cyprus.initialize()
        if (cyprus.read_gpio() & 0b0010):
            cyprus.set_pwm_values(2, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        else:
            cyprus.set_pwm_values(2, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        cyprus.close()


    def talon_dc(self):
        cyprus.initialize()
        cyprus.setup_servo(1)
        cyprus.set_servo_speed(1, 1)
        sleep(1)
        cyprus.set_servo_speed(1, 0)
        sleep(5)
        cyprus.set_servo_speed(1, -1)
        sleep(1)
        cyprus.set_servo_speed(1, 0)
        cyprus.close()

    def ramp_up(self):
        cyprus.initialize()
        cyprus.setup_servo(1)
        for i in range(2, 4, 6, 8, 10):
            cyprus.set_servo_speed(1, i/10.0)
            sleep(4)
        cyprus.set_servo_position(1, 0.5)
        cyprus.close()


    def shutdown(self):
        s0.free_all()
        spi.close()
        GPIO.cleanup()
        os.system("sudo shutdown now")


    def pressed(self):
        """
        Function called on button touch event for button with id: testButton
        :return: None
        """
        PauseScreen.pause(pause_scene_name='pauseScene', transition_back_scene='main', text="Test", pause_duration=5)

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'


class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()
"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()

MixPanel



def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()
