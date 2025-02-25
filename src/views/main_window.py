import toga
import time
import sys
import os
import asyncio
import pyperclip
import re
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

# Modifier l'import pour qu'il fonctionne avec PyInstaller
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.totp import generate_totp_secret  # Import relatif depuis le dossier parent

if getattr(sys, 'frozen', False):
    # Si le programme est exécuté en tant qu'exécutable
    base_path = sys._MEIPASS  # Répertoire temporaire créé par PyInstaller
else:
    # Si le programme est exécuté en tant que script Python normal
    base_path = os.path.dirname(os.path.dirname(__file__))


LOGO = os.path.join(base_path, 'resources','TOTP.png')
CLIPBOARD = os.path.join(base_path, 'resources','clipboard.png')
CLIPBOARD_COPY = os.path.join(base_path, 'resources','clipboard-1.png')

class MainWindow(toga.MainWindow):
    def __init__(self, title, app):
        super().__init__(
            title,
            size=(300, 470),
            resizable=False
        )
        
        self.update_task = None
        
        # Création des widgets
        self.secret_input = toga.TextInput(style=Pack(flex=1))
        self.period_input = toga.NumberInput(value=30, min=1, style=Pack(flex=1))
        self.digits_input = toga.NumberInput(value=6, min=6, max=8, style=Pack(flex=1))
        
        # Liste déroulante pour les algorithmes
        self.algo_selection = toga.Selection(
            items=["sha3_512",
                   "blake2s",
                   "sm3",
                   "md5-sha1",
                   "shake_128",
                   "sha384",
                   "sha512_224",
                   "sha3_384",
                   "blake2b",
                   "sha1",
                   "sha256",
                   "sha512_256",
                   "sha3_256",
                   "sha3_224",
                   "md5",
                   "sha224",
                   "sha512",
                   "ripemd160",
                   "shake_256"
                   ],
            value="sha1",
            style=Pack(flex=1)
        )
        self.time = toga.ProgressBar(max=100, value=0, style=Pack(padding_top=3,flex=1))
        
        self.result_label = toga.Label('------', style=Pack(font_weight="bold",text_align="center", font_size=45,flex=1))
        
        # Bouton de génération
        generate_button = toga.Button('Générer', style=Pack(flex=1), on_press=self.generate_totp)
        
        # Bouton de copie
        self.copy_button = toga.Button(icon=CLIPBOARD, style=Pack(width=30,flex=1), on_press=self.copy_to_clipboard)
        self.copy_button.enabled = False
        
        # Layout
        input_box = toga.Box(
            children=[
                toga.Box(
                    children=[
                        toga.ImageView(LOGO, style=Pack(width=90, height=90, flex=1)),
                        #toga.Label('TOTP', style=Pack(alignment="center", text_align="center", font_weight="bold", font_size=45, flex=1)),
                        ],
                     style=Pack(direction=COLUMN, alignment="center", padding=5)),
                toga.Box(
                    children=[
                        toga.Divider(),
                        self.result_label,
                        toga.Divider()
                        ],
                    style=Pack(direction=COLUMN, padding=5)
                ),
                toga.Box(
                    children=[
                        self.time,
                        self.copy_button
                        ],
                    style=Pack(direction=ROW, padding=5)
                ),
                toga.Box(
                    children=[
                        toga.Label('Secret (key/otpauth):',style=Pack(flex=1)),
                    ],
                    style=Pack(direction=ROW, padding=5)
                ),
                toga.Box(
                    children=[
                        self.secret_input
                    ],
                    style=Pack(direction=ROW, padding=5)
                ),
                toga.Box(
                    children=[
                        toga.Label('Période (sec):', style=Pack(flex=1)),
                        self.period_input
                    ],
                    style=Pack(direction=ROW, padding=5)
                ),
                toga.Box(
                    children=[
                        toga.Label('Nombre de chiffres:', style=Pack(flex=1)),
                        self.digits_input
                    ],
                    style=Pack(direction=ROW, padding=5)
                ),
                toga.Box(
                    children=[
                        toga.Label('Algorithme:', style=Pack(flex=1)),
                        self.algo_selection
                    ],
                    style=Pack(direction=ROW, padding=5)
                ),
                toga.Box(
                    children=[generate_button],
                    style=Pack(direction=ROW, padding=5)
                ),
            ],
            style=Pack(direction=COLUMN, padding=10)
        )
        
        # Correction du pattern regex pour les URI TOTP
        self.totp_uri_pattern = re.compile(
            r'^otpauth://totp/(?:(?P<issuer>[^:]+):)?(?P<name>[^?]+)'
            r'\?secret=(?P<secret>[A-Z2-7=]+)'
            r'(?:&issuer=(?P<issuer_2>[^&]+))?'
            r'(?:&algorithm=(?P<algorithm>[^&]+))?'
            r'(?:&digits=(?P<digits>\d+))?'
            r'(?:&period=(?P<period>\d+))?$'
        )
        
        self.content = input_box

    def parse_totp_uri(self, uri: str) -> dict:
        """Parse une URI TOTP et retourne les paramètres"""
        match = self.totp_uri_pattern.match(uri)
        if not match:
            raise ValueError("URI TOTP invalide")
            
        params = match.groupdict()
        return {
            'secret': params['secret'],
            'algorithm': params.get('algorithm', 'SHA1') if params.get('algorithm') else 'SHA1',
            'digits': int(params.get('digits')) if params.get('digits') else 6,
            'period': int(params.get('period')) if params.get('period') else 30,
            'issuer': params.get('issuer') or params.get('issuer_2', '')
        }

    def generate_totp(self, widget):
        try:
            
            secret = self.secret_input.value.strip()
            
            # Vérifier si c'est une URI TOTP
            if secret.startswith('otpauth://totp/'):
                try:
                    params = self.parse_totp_uri(secret)
                    secret = params['secret']
                    # Mettre à jour les widgets avec les valeurs de l'URI
                    self.period_input.value = params['period']
                    self.digits_input.value = params['digits']
                    self.algo_selection.value = str(params['algorithm']).lower()
                except ValueError as ve:
                    raise ValueError(f"URI TOTP invalide: {str(ve)}")
            
            if not secret:
                raise ValueError("Secret requis")
            
            # Récupération et validation des valeurs numériques
            try:
                period = int(self.period_input.value or 30)  # Valeur par défaut si None
                digits = int(self.digits_input.value or 6)   # Valeur par défaut si None
            except (ValueError, TypeError):
                raise ValueError("Les valeurs de période et digits doivent être des nombres")
                
            algo = self.algo_selection.value or 'sha1'  # Valeur par défaut si None
            
            code = generate_totp_secret(
                secret_key=secret,
                algo=algo,
                digits=digits,
                period=period
            )
            
            self.result_label.text = f"{code}"
            self.copy_button.enabled = True
            # Démarrer la mise à jour automatique
            if self.update_task is None:
                self.update_task = self.app.loop.create_task(self.auto_update())
            
        except ValueError as ve:
            self.app.loop.create_task(self.informations("Erreur", str(ve)))
        except Exception as e:
            self.app.loop.create_task(self.informations("Erreur", str(e)))
            
    async def informations(self, title, message):
        """Affiche une boîte de dialogue d'informations"""
    
        dialog = toga.InfoDialog(
                title=title,
                message=str(message),
                
            )
        await toga.Window.dialog(self, dialog)

    async def auto_update(self):
        """Met à jour le code TOTP automatiquement"""
        while True:
            try:
                # Attendre jusqu'à la prochaine période
                period = int(self.period_input.value)
                wait_time = period - (time.time() % period)
                
                # Mise à jour de la barre de progression toutes les secondes
                for i in range(int(wait_time)):
                    self.time.value = int(100 - ((i / wait_time) * 100))
                    await asyncio.sleep(1)  # Attendre 1 seconde
                
                # Assurer que la barre atteint 100% avant de régénérer
                self.time.value = 0
                self.copy_button.icon = CLIPBOARD
                # Regénérer le code
                await asyncio.sleep(0.1)  # Petit délai pour voir la barre à 100%
                if self.secret_input.value:
                    self.generate_totp(None)
                else:
                    self.time.value = 0
                    self.result_label.text = "------"
                    self.update_task = None
                    self.copy_button.enabled = False
                    break
                
            except Exception as e:
                print(f"Erreur lors de la mise à jour automatique: {e}")
                self.time.value = 0
                break
            
    def copy_to_clipboard(self, widget):
        """Copie le code TOTP dans le presse-papier"""
        try:
            # Extraire le code du label (enlever le préfixe "Code TOTP: ")
            code = self.result_label.text
            self.copy_button.icon = CLIPBOARD_COPY
            # Vérifier si un code existe
            if code and code != "":
                # Utiliser pyperclip pour la compatibilité multi-plateforme
                pyperclip.copy(code)
                # Feedback temporaire
                self.app.loop.create_task(self.informations("Info", "Code copié !"))
                
        except Exception as e:
            print(f"Erreur lors de la copie: {e}")

def main():
    return MainWindow("TOTP Generator", None)