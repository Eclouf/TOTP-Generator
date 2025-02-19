
import toga
import os
import sys

if getattr(sys, 'frozen', False):
    # Si le programme est exécuté en tant qu'exécutable
    base_path = sys._MEIPASS  # Répertoire temporaire créé par PyInstaller
else:
    # Si le programme est exécuté en tant que script Python normal
    base_path = os.path.dirname(__file__)


LOGO = os.path.join(base_path, 'resources','TOTP.png')

from views import main_window 

class TOTPApp(toga.App):
    def startup(self):
        self.main_window = main_window.MainWindow('TOTP Generator', self)
        self.main_window.show()

if __name__ == '__main__':
    app = TOTPApp(
        formal_name='TOTP Generator',
        app_id='org.example.totp',
        app_name='TOTP Generator',
        icon=LOGO,
        author="Eclouf",
        version=" 0.0.1",
        home_page="https://github.com/Eclouf/TOTP-Generator",
        description="A simple TOTP generator",
        )
    app.main_loop()
    