import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path
import re
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import stat

def is_windows():
    return platform.system() == "Windows"

def get_sdk_root():
    """Get appropriate SDK root path for the platform"""
    if is_windows():
        return Path.home() / "AppData" / "Local" / "Android" / "Sdk"
    else:
        # Standard Linux location or allow override with ANDROID_HOME
        return Path(os.environ.get("ANDROID_HOME", str(Path.home() / "Android" / "Sdk")))

# Config
sdk_root = get_sdk_root()
cmdline_tools_dir = sdk_root / "cmdline-tools"
latest_dir = cmdline_tools_dir / "latest"

def run(cmd, cwd=None):
    """Run command with platform-appropriate settings"""
    print(f"[RUN] {cmd}")
    if isinstance(cmd, str) and not is_windows():
        cmd = cmd.split()  # On Linux, better to pass as list
    subprocess.run(cmd, shell=is_windows(), check=True, cwd=cwd)

def find_executable(base_path, base_name):
    """
    Find the executable file with platform-specific extensions
    """
    extensions = [".exe", ".bat", ".cmd", ""] if is_windows() else ["", ".sh"]
    for ext in extensions:
        path = base_path / (base_name + ext)
        if path.is_file():
            return str(path)
    raise FileNotFoundError(f"Could not find {base_name} with extensions {extensions} in {base_path}")

def get_available_system_images():
    """Extracts available system images from `sdkmanager --list` output."""
    sdkmanager_path = find_executable(latest_dir / "bin", "sdkmanager")
    if not sdkmanager_path:
        return []

    result = subprocess.run([sdkmanager_path, "--list"], capture_output=True, text=True)
    output = result.stdout
    pattern = r'(system-images;[^\s]+)'
    matches = re.findall(pattern, output)
    return matches

def install_sdk_components(sdkmanager_path, system_image, platform_version):
    print("[*] Accepting licenses...")
    run([sdkmanager_path, f"--sdk_root={sdk_root}", "--licenses"])

    print("[*] Installing system image and platform SDK...")
    run([sdkmanager_path, f"--sdk_root={sdk_root}", f"platforms;{platform_version}", system_image])

def create_avd(system_image, avd_name):
    """Create Android Virtual Device"""
    avdmanager_path = find_executable(latest_dir / "bin", "avdmanager")
    sdkmanager_path = find_executable(latest_dir / "bin", "sdkmanager")
    
    if not avdmanager_path:
        print(f"[!] avdmanager not found at {latest_dir / 'bin'}")
        return 
    
    # Install the specific system image
    run([sdkmanager_path, system_image])
    
    # Create the AVD
    device = "pixel"
    run([avdmanager_path, "create", "avd", "-n", avd_name, "-k", system_image, "--device", device])

def get_installed_emulators():
    """Returns list of installed emulators"""
    emulator_path = find_executable(sdk_root / "emulator", "emulator")
    if not emulator_path:
        return []
    
    result = subprocess.run([emulator_path, "-list-avds"], capture_output=True, text=True)
    return result.stdout.strip().splitlines()

def run_emulator(avd_name):
    """Launch the specified emulator"""
    emulator_path = find_executable(sdk_root / "emulator", "emulator")
    if not emulator_path:
        print("[!] Emulator not found")
        return
    
    # On Linux, run in background with nohup
    if not is_windows():
        cmd = f"nohup {emulator_path} -avd {avd_name} >/dev/null 2>&1 &"
        os.system(cmd)
    else:
        subprocess.Popen([emulator_path, "-avd", avd_name])

def create_launcher_shortcut():
    """Create a desktop shortcut to this script itself (first-time setup)"""
    script_path = os.path.abspath(__file__)
    
    if not is_windows():
        print("[*] Creating AVD Launcher desktop shortcut...")
        desktop_path = Path.home() / "Desktop"
        if not desktop_path.exists():
            print("[!] Could not find desktop directory")
            return False
        
        shortcut_path = desktop_path / "Android_AVD_Launcher.desktop"
        
        # Check if shortcut already exists
        if shortcut_path.exists():
            print("[+] AVD Launcher shortcut already exists")
            return True
        
        content = f"""[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Exec={sys.executable} {script_path}
Name=Android AVD Launcher
Comment=Manage and launch Android Virtual Devices
Icon=android
Categories=Development;
"""
        try:
            with open(shortcut_path, "w") as f:
                f.write(content)
            
            # Make executable
            shortcut_path.chmod(shortcut_path.stat().st_mode | stat.S_IEXEC)
            print(f"[+] Created AVD Launcher shortcut at {shortcut_path}")
            return True
        except Exception as e:
            print(f"[!] Failed to create launcher shortcut: {e}")
            return False
    
    # Windows shortcut creation
    try:
        import pythoncom
        from win32com.shell import shell, shellcon
        from win32com.client import Dispatch
    except ImportError:
        print("[!] pywin32 not available. Skipping launcher shortcut creation.")
        return False

    desktop_path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
    shortcut_path = os.path.join(desktop_path, "Android AVD Launcher.lnk")
    
    # Check if shortcut already exists
    if os.path.exists(shortcut_path):
        print("[+] AVD Launcher shortcut already exists")
        return True
    
    try:
        shell_obj = Dispatch('WScript.Shell')
        shortcut = shell_obj.CreateShortcut(shortcut_path)
        shortcut.TargetPath = sys.executable
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = str(Path(script_path).parent)
        shortcut.IconLocation = sys.executable
        shortcut.Description = "Manage and launch Android Virtual Devices"
        shortcut.Save()
        print(f"[+] Created AVD Launcher shortcut at: {shortcut_path}")
        return True
    except Exception as e:
        print(f"[!] Failed to create launcher shortcut: {e}")
        return False

def create_desktop_shortcut(avd_name):
    if not is_windows():
        print("[*] Creating desktop shortcut on Linux...")
        desktop_path = Path.home() / "Desktop"
        if not desktop_path.exists():
            desktop_path = Path.home() / "Desktop"
            if not desktop_path.exists():
                print("[!] Could not find desktop directory")
                return
        
        shortcut_path = desktop_path / f"Launch_{avd_name}.desktop"
        emulator_path = sdk_root / "emulator" / "emulator"
        
        content = f"""[Desktop Entry]
                        Version=1.0
                        Type=Application
                        Terminal=false
                        Exec={emulator_path} -avd {avd_name}
                        Name=Launch {avd_name}
                        Icon=android
                        """
        with open(shortcut_path, "w") as f:
            f.write(content)
        
        # Make executable
        shortcut_path.chmod(shortcut_path.stat().st_mode | stat.S_IEXEC)
        print(f"[+] Created desktop shortcut at {shortcut_path}")
        return
        
    # Windows shortcut creation
    try:
        import pythoncom
        from win32com.shell import shell, shellcon
        from win32com.client import Dispatch
    except ImportError:
        print("[!] pywin32 not available. Skipping shortcut creation.")
        return

    desktop_path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
    shortcut_path = os.path.join(desktop_path, f"Launch {avd_name}.lnk")

    target = sdk_root / "emulator" / "emulator.exe"
    if not target.exists():
        print(f"[!] Emulator executable not found at {target}")
        return

    arguments = f"-avd {avd_name}"
    working_dir = target.parent
    icon = str(target)

    shell_obj = Dispatch('WScript.Shell')
    shortcut = shell_obj.CreateShortcut(shortcut_path)
    shortcut.TargetPath = str(target)
    shortcut.Arguments = arguments
    shortcut.WorkingDirectory = str(working_dir)
    shortcut.IconLocation = icon
    shortcut.Save()

    print(f"[+] Desktop shortcut created at: {shortcut_path}")

def create_avd_name(system_image):
    parts = system_image.split(";")
    android_version = parts[1].replace("android-", "API_")
    return f"Pixel{android_version}"

def prompt_gui():
    def on_run():
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select an installed emulator to run.")
            return
        selected = listbox.get(selected_indices[0])
        root.selected_emulator = f"IE_{selected}"
        root.destroy()

    def open_available_emulators():
        def on_install():
            selected_indices = avail_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select an emulator to install.")
                return
            selected = avail_listbox.get(selected_indices[0])
            root.selected_emulator = f"AE_{selected}"
            avail_root.destroy()
            root.destroy()

        avail_root = tk.Toplevel(root)
        avail_root.title("Available Emulators")
        avail_root.geometry("750x550")

        title = tk.Label(avail_root, text="Available Emulators", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)

        avail_listbox = tk.Listbox(avail_root, font=("Segoe UI", 12), height=15, width=70, bg="white", selectbackground="#0066CC")
        avail_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        emulators = get_available_system_images()
        if isinstance(emulators, str):
            emulators = emulators.strip().splitlines()

        for emu in emulators:
            avail_listbox.insert(tk.END, emu)

        install_button = tk.Button(avail_root, text="Install", command=on_install, font=("Segoe UI", 12, "bold"), bg="#4CAF50", fg="white", padx=20, pady=5)
        install_button.pack(pady=15)

        avail_root.transient(root)
        avail_root.grab_set()
        root.wait_window(avail_root)

    root = tk.Tk()
    root.title("Installed Emulators")
    root.geometry("750x550")

    # Top bar with "+" button
    top_frame = tk.Frame(root)
    top_frame.pack(fill=tk.X, padx=10, pady=10)

    title = tk.Label(top_frame, text="Installed Emulators", font=("Segoe UI", 14, "bold"))
    title.pack(side=tk.LEFT)

    plus_button = tk.Button(top_frame, text="+", font=("Segoe UI", 14), command=open_available_emulators)
    plus_button.pack(side=tk.RIGHT)

    # Main List
    listbox = tk.Listbox(root, font=("Segoe UI", 12), height=15, width=70, bg="white", selectbackground="#0066CC")
    listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

    emulators = get_installed_emulators()
    if isinstance(emulators, str):
        emulators = emulators.strip().splitlines()

    for emu in emulators:
        listbox.insert(tk.END, emu)

    run_button = tk.Button(root, text="Run", command=on_run, font=("Segoe UI", 12, "bold"), bg="#4CAF50", fg="white", padx=20, pady=5)
    run_button.pack(pady=15)

    root.mainloop()

    return getattr(root, "selected_emulator", None)

def check_dependencies():
    """Check for required dependencies on Linux"""
    if is_windows():
        return True
    
    required = ["unzip", "java"]
    missing = []
    for cmd in required:
        if shutil.which(cmd) is None:
            missing.append(cmd)
    
    if missing:
        print(f"[!] Missing required commands: {', '.join(missing)}")
        print("On Ubuntu/Debian, run: sudo apt install unzip openjdk-11-jdk")
        return False
    return True

def main():
    if not is_windows() and not check_dependencies():
        return
    
    # Create launcher shortcut on first run
    create_launcher_shortcut()

    selection = prompt_gui()
    if not selection:
        return

    if selection.startswith('IE_'):
        print("Launching your emulator")
        avd_name = selection[3:]
        run_emulator(avd_name)
    else:
        system_image = selection[3:] 
        avd_name = create_avd_name(system_image)
        platform_version = system_image.split(";")[1]
        
        sdkmanager_path = find_executable(latest_dir / "bin", "sdkmanager")
        if not sdkmanager_path:
            print("[!] Could not find sdkmanager")
            return
            
        install_sdk_components(sdkmanager_path, system_image, platform_version)
        create_avd(system_image, avd_name)
        create_desktop_shortcut(avd_name)
        
        print("\n✅ Setup complete!")
        print(f"➡️  To launch the emulator manually, run:")
        print(f"    {sdk_root}/emulator/emulator -avd {avd_name}")
        if is_windows():
            print("➡️  Or double-click the desktop shortcut")

if __name__ == "__main__":
    main()