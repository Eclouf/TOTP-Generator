import subprocess
import sys
import os
import platform
import re
import datetime

def check_os():
    return platform.system()

def check_pyinstaller():
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    print("PyInstaller is not installed. Installation in progress...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller has been successfully installed!")
        return True
    except subprocess.CalledProcessError:
        print("Error installing PyInstaller.")
        return False

def get_user_choice(prompt, options):
    while True:
        choice = input(f"{prompt} ({'/'.join(options)}): ").lower()
        if choice in options:
            return choice
        print(f"Invalid choice. Please select one: {', '.join(options)}")

def update_changelog():
    """Gère la mise à jour du changelog"""
    changelog_file = "CHANGELOG.md"
    version_file = "version.txt"
    
    if os.path.exists(changelog_file):
        with open(changelog_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Extraire la dernière version
        version_match = re.search(r"## \[(\d+\.\d+\.\d+)\]", content)
        if version_match:
            current_version = version_match.group(1)
            print(f"Current version: {current_version}")
            
            # Proposer une incrémentation automatique
            major, minor, patch = map(int, current_version.split('.'))
            print("\nAvailable update types:")
            print(f"1. Major: {major + 1}.0.0")
            print(f"2. Minor: {major}.{minor + 1}.0")
            print(f"3. Correction: {major}.{minor}.{patch + 1}")
            print("4. Customized version")
            
            choice = get_user_choice("Choose the type of update", ["1", "2", "3", "4"])
            
            if choice == "1":
                new_version = f"{major + 1}.0.0"
            elif choice == "2":
                new_version = f"{major}.{minor + 1}.0"
            elif choice == "3":
                new_version = f"{major}.{minor}.{patch + 1}"
            else:
                while True:
                    new_version = input("Enter the new version (format X.Y.Z): ")
                    if re.match(r"^\d+\.\d+\.\d+$", new_version):
                        break
                    print("Invalid format. Use X.Y.Z format")
            
            # Demander les modifications
            print("\nEnter changes (one per line, blank line to end):")
            changes = []
            while True:
                change = input("- ")
                if not change:
                    break
                changes.append(change)
            
            # Créer la nouvelle entrée
            new_entry = f"\n## [{new_version}] - {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
            if changes:
                new_entry += "\n### Modifications\n"
                for change in changes:
                    new_entry += f"- {change}\n"
            
            # Insérer la nouvelle entrée après le titre
            content = re.sub(r"(# Changelog\n)", f"\\1\n{new_entry}", content)
            
            with open(version_file, 'r', encoding='utf-8') as f:
                version_text = f.read()
                print(version_text)
                version_text = re.sub(r"StringStruct\('ProductVersion', '(.*?)'\),", f"StringStruct(\'ProductVersion\', \'{new_version}\'),", version_text)
                print(version_text)
            with open(version_file, 'w', encoding='utf-8') as f:
                f.write(version_text)
            
        else:
            print("No version found in changelog")
            new_version = input("Enter the new version (format X.Y.Z): ")
            content = f"# Changelog\n\n## [{new_version}] - {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
    else:
        print("Création du changelog initial")
        new_version = input("Enter the new version (format X.Y.Z): ")
        content = f"# Changelog\n\n## [{new_version}] - {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
    
    # Sauvegarder les modifications
    with open(changelog_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    return new_version

def main():
    if not check_pyinstaller():
        install = get_user_choice("PyInstaller is not installed. Would you like to install it?", ["oui", "non"])
        if install == "non":
            print("Impossible to continue without PyInstaller!")
            return
        if not install_pyinstaller():
            return
    # Mise à jour du changelog avant la compilation
    update_changelog()
    
    # Options de compilation
    onefile = get_user_choice("Do you want to compile to a single file?", ["oui", "non"])
    console = get_user_choice("Do you want to keep the console visible?", ["oui", "non"])
    
    # Mise à jour du changelog avant la compilation
    update_changelog()
    
    # Construction de la commande PyInstaller
    cmd = ["pyinstaller"]
    if onefile == "oui":
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")
    
    if console == "non":
        cmd.append("--noconsole")
    
    # Ajout des options spécifiques au projet
    if check_os() == "Windows":
        print("Compilation for Windows...")
        cmd.append("--version-file=version.txt")
        #cmd.append("--manifest=manifest.xml")
    elif check_os() == "Darwin":
        print("Compilation for macOS...")
        cmd.append("--osx-bundle-identifier=com.eclouf.audeo")
        cmd.append("--target-architecture=universal")
        cmd.append("--osx-entitlements-file=entitlements.plist")
        
    cmd.extend([
        "--name", "TOTP Generator",
        "--icon=src/resources/TOTP.ico",
        "--add-data=src/resources:resources",
        "--add-data=src/views:views",
        '--hidden-import=src.totp', 
        "--hidden-import=pyperclip",
        "src/app.py"
    ])

    print("\nStart of compilation...")
    try:
        print("Commande PyInstaller:", " ".join(cmd))
        subprocess.check_call(cmd)
        print("\nCompilation successfully completed!")
        print("The executable file is located in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\nCompilation error: {e}")

if __name__ == "__main__":
    main()
