
import toga
from .views.main_window import MainWindow

class TOTPApp(toga.App):
    def startup(self):
        self.main_window = MainWindow('TOTP Generator', self)
        self.main_window.show()

if __name__ == '__main__':
    app = TOTPApp('TOTP Generator', 'org.example.totp', icon="resources/TOTP.png")
    app.main_loop()
    