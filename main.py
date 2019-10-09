import os

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.slider import Slider
from kivy.animation import Animation
from time import sleep


from threading import Thread

from pidev.Joystick import Joystick
from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'
FARMYARD_SCREEN_NAME = 'farm'

joystick = Joystick(0, False)
"""while 1:
    print(str(joystick.get_axis('x')))
    sleep(.1) 
"""


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
    label_text = StringProperty()
    braedan = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.count = 0
        self.braedan = False
        self.label_text = str(self.count)

    def increment(self, *args):
        self.count += 1
        self.label_text = str(self.count)
        print(self.label_text)

    def motor(self):
        self.braedan = not self.braedan

    def pressed(self):
        """
        Function called on button touch event for button with id: testButton
        :return: None
        """
        PauseScreen.pause(pause_scene_name='pauseScene', transition_back_scene='main', text="Test", pause_duration=1)

    def clicked(self):
        PauseScreen.pause(pause_scene_name='pauseScene', transition_back_scene='farm', text="Test", pause_duration=1)

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'


class Farmyard(Screen):

    joystick = Joystick(0, True)
    joy_val_x = ObjectProperty(0)
    joy_val_y = ObjectProperty(0)
    joy_trigger_label = ObjectProperty(0)


    def __init__(self, **kwargs):
        Builder.load_file('Farmyard.kv')

        PassCodeScreen.set_transition_back_screen(MAIN_SCREEN_NAME)

        super(Farmyard, self).__init__(**kwargs)

    def update(self):

        while 1:
            self.joy_val_x = joystick.get_axis('x')
            self.joy_val_y = joystick.get_axis('y')
            self.joy_trigger_label = self.joystick.get_button_state(0)
            sleep(.1)

    def joy_thread(self):
        Thread(target=self.update, args=()).start()


    def transition_back(self):

        SCREEN_MANAGER.current = MAIN_SCREEN_NAME


    def back(self):

        PauseScreen.pause(pause_scene_name='pauseScene', transition_back_scene='main', text="Test", pause_duration=5)

    """
        Function called on button touch event for button with id: testButton
        :return: None
    """
    def animation(self):
        anim = Animation(x=50, y=50) & Animation(size=(200, 200))

        anim.start(self.ids.logo_image_button)









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
# Builder.load_file('Farmyard.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(Farmyard(name=FARMYARD_SCREEN_NAME))
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
