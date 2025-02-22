"""
A modern graphical user interface for generating TOTP (Time-based One-Time Password) codes according to RFC 6238.
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from views import main_window 


class TOTPGenerator(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.main_window = main_window.MainWindow("TOTP Generator", self)
        self.main_window.show()


def main():
    return TOTPGenerator()
