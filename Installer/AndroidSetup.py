import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path
import re
import platform
import stat
import tempfile
import json
import ctypes

# Check and install tkinter if missing
def check_and_install_tkinter():
    """Check if tkinter is available, install if missing on Linux"""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        return True
    except ImportError:
        if platform.system() != "Windows":
            print("[!] tkinter is not installed.")
            print("[*] Installing python3-tk...")
            try:
                subprocess.run(["apt", "update"], check=True)
                subprocess.run(["apt", "install", "-y", "python3-tk"], check=True)
                print("[+] python3-tk installed successfully")
                print("[*] Continuing with setup...")
                # Try importing again after installation
                try:
                    import tkinter as tk
                    from tkinter import ttk, messagebox
                    return True
                except ImportError:
                    print("[!] tkinter still not available after installation")
                    print("[!] Please restart the script")
                    return False
            except subprocess.CalledProcessError:
                print("[!] Failed to install python3-tk automatically")
                print("[!] Please install it manually:")
                print("    sudo apt update")
                print("    sudo apt install python3-tk")
                print("[!] Then run the script again")
                return False
        else:
            print("[!] tkinter is not available. Please reinstall Python with tkinter support.")
            return False

# Check tkinter before importing
if not check_and_install_tkinter():
    sys.exit(1)

import tkinter as tk
from tkinter import ttk, messagebox

def is_windows():
    return platform.system() == "Windows"

def is_admin():
    """Check if the script is running with administrator/root privileges"""
    if is_windows():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        # Linux/Unix - check if running as root
        return os.geteuid() == 0

def run_as_admin():
    """Restart the script with administrator/root privileges"""
    if is_windows():
        print("[!] Administrator privileges required. Requesting elevation...")
        try:
            # Re-run the script with admin privileges
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:])
            
            # Use ShellExecuteW to request elevation
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas",  # Request elevation
                sys.executable,  # Python executable
                params,  # Script and arguments
                None,  # Working directory
                1  # Show window
            )
            sys.exit(0)
        except Exception as e:
            print(f"[!] Failed to elevate privileges: {e}")
            print("[!] Please run this script as Administrator manually.")
            sys.exit(1)
    else:
        # Linux - use sudo
        print("[!] Root privileges required. Requesting sudo...")
        try:
            args = ['sudo', sys.executable] + sys.argv
            os.execvp('sudo', args)
        except Exception as e:
            print(f"[!] Failed to elevate privileges: {e}")
            print("[!] Please run this script with sudo manually:")
            print(f"    sudo python3 {sys.argv[0]}")
            sys.exit(1)

def install_pywin32_if_missing():
    if not is_windows():
        return
    try:
        import win32com
    except ImportError:
        print("[*] pywin32 not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
        print("[+] pywin32 installed successfully.")

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

def get_sdk_root():
    """Get appropriate SDK root path for the platform"""
    if is_windows():
        return Path.home() / "AppData" / "Local" / "Android" / "Sdk"
    else:
        # Use user directory by default to avoid permission issues
        user_sdk = Path.home() / "Android" / "Sdk"
        
        # Check if ANDROID_HOME is already set
        if os.environ.get("ANDROID_HOME"):
            return Path(os.environ.get("ANDROID_HOME"))
        
        # Create user directory
        user_sdk.mkdir(parents=True, exist_ok=True)
        print("[*] Using user Android SDK location: ~/Android/Sdk")
        return user_sdk

# Config
sdk_root = get_sdk_root()
cmdline_tools_version = "10406996_latest"

# Different download URL for Linux vs Windows
if is_windows():
    cmdline_tools_zip_url = f"https://dl.google.com/android/repository/commandlinetools-win-{cmdline_tools_version}.zip"
else:
    cmdline_tools_zip_url = f"https://dl.google.com/android/repository/commandlinetools-linux-{cmdline_tools_version}.zip"

cmdline_zip_path = sdk_root / "cmdline-tools.zip"
cmdline_tools_dir = sdk_root / "cmdline-tools"
latest_dir = cmdline_tools_dir / "latest"

def ensure_dirs():
    print(f"[*] Ensuring directory exists: {latest_dir}")
    latest_dir.mkdir(parents=True, exist_ok=True)

def download_cmdline_tools():
    if cmdline_zip_path.exists():
        print("[+] Command line tools archive already downloaded.")
        return
    
    print("[*] Downloading Android Command Line Tools...")
    try:
        urllib.request.urlretrieve(cmdline_tools_zip_url, cmdline_zip_path, download_progress_hook)
        print("\n[+] Download complete.")
    except Exception as e:
        print(f"\n[!] Download failed: {e}")
        if not is_windows():
            print("You can try manually downloading with:")
            print(f"wget {cmdline_tools_zip_url} -O {cmdline_zip_path}")
        sys.exit(1)

def extract_cmdline_tools():
    if (latest_dir / "bin" / "sdkmanager").exists() or (latest_dir / "bin" / "sdkmanager.bat").exists():
        print("[+] Command line tools already extracted.")
        if cmdline_zip_path.exists():
            cmdline_zip_path.unlink()
        return

    print("[*] Extracting command line tools...")
    try:
        with zipfile.ZipFile(cmdline_zip_path, 'r') as zip_ref:
            zip_ref.extractall(latest_dir)

        inner_path = latest_dir / "cmdline-tools"
        if inner_path.is_dir():
            for item in inner_path.iterdir():
                shutil.move(str(item), latest_dir)
            shutil.rmtree(inner_path)

        if cmdline_zip_path.exists():
            cmdline_zip_path.unlink()
        
        # Make binaries executable on Linux
        if not is_windows():
            bin_dir = latest_dir / "bin"
            for tool in bin_dir.glob("*"):
                if tool.is_file():
                    tool.chmod(tool.stat().st_mode | stat.S_IEXEC)
        
        print("[+] Extraction complete.")
    except Exception as e:
        print(f"[!] Extraction failed: {e}")
        sys.exit(1)

def set_env_vars():
    print("[*] Setting environment variables...")
    
    # Set ANDROID_HOME and update PATH
    env_update = {
        "ANDROID_HOME": str(sdk_root),
        "PATH": [
            str(sdk_root / "platform-tools"),
            str(sdk_root / "emulator"),
            str(latest_dir / "bin")
        ]
    }
    
    if is_windows():
        try:
            import winreg
            # Set ANDROID_HOME system variable
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                               0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "ANDROID_HOME", 0, winreg.REG_EXPAND_SZ, str(sdk_root))
                print("[+] ANDROID_HOME set in Windows registry")

            # Update PATH system variable
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                               0, winreg.KEY_ALL_ACCESS) as key:
                current_path, _ = winreg.QueryValueEx(key, "Path")
                path_parts = current_path.split(";")
                updated = False

                for p in env_update["PATH"]:
                    if p not in path_parts:
                        path_parts.append(p)
                        updated = True

                if updated:
                    new_path = ";".join(path_parts)
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    print("[+] PATH updated in Windows registry")
        except Exception as e:
            print(f"[!] Failed to update Windows registry: {e}")
            print("You may need to run this script as administrator")
    else:
        # Linux - determine if system-wide or user installation
        is_system_wide = str(sdk_root).startswith('/opt/')
        
        # Use current user's home directory
        user_home = Path.home()
        print("[*] Setting Android environment variables for current user")
        
        if is_system_wide:
            print("[*] System-wide Android SDK installation detected")
        else:
            print("[*] User-specific Android SDK installation detected")
        
        shell_configs = [
            user_home / ".bashrc",
            user_home / ".zshrc",
            user_home / ".profile"
        ]
        
        export_lines = [
            f"export ANDROID_HOME={sdk_root}",
            f"export PATH={':'.join(env_update['PATH'])}:$PATH"
        ]
        
        # Set environment variables in current session
        os.environ['ANDROID_HOME'] = str(sdk_root)
        current_path = os.environ.get('PATH', '')
        for path_item in env_update['PATH']:
            if path_item not in current_path:
                current_path = f"{path_item}:{current_path}"
        os.environ['PATH'] = current_path
        
        updated = False
        for config_file in shell_configs:
            if config_file.exists():
                try:
                    with open(config_file, 'r+') as f:
                        content = f.read()
                        needs_update = any(export not in content for export in export_lines)
                        
                        if needs_update:
                            f.write("\n# Android SDK paths\n" + "\n".join(export_lines) + "\n")
                            print(f"[+] Updated {config_file} with Android paths")
                            updated = True
                except Exception as e:
                    print(f"[!] Failed to update {config_file}: {e}")
        
        if updated:
            print("[!] Please restart your terminal or run 'source ~/.bashrc' (or your shell config)")
        else:
            print("[+] Environment variables already set")

def install_sdk_components(sdkmanager_path, system_image, platform_version):
    print("[*] Accepting licenses...")
    run([sdkmanager_path, f"--sdk_root={sdk_root}", "--licenses"])

    print("[*] Installing platform-tools, emulator, platform SDK, tools, and system image...")
    run([sdkmanager_path, f"--sdk_root={sdk_root}", 
         "platform-tools",  # Contains essential tools like adb
         "emulator",        # The Android emulator
         "tools",          # Legacy SDK tools
         f"platforms;{platform_version}",  # Android platform SDK
         system_image])    # System image for the emulator

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
    
    if is_windows():
        subprocess.Popen([emulator_path, "-avd", avd_name])
    else:
        # Linux - run in background and detach
        cmd = f"nohup {emulator_path} -avd {avd_name} >/dev/null 2>&1 &"
        os.system(cmd)
    print(f"[+] Emulator {avd_name} launched")

def create_desktop_shortcut(avd_name):
    if not is_windows():
        print("[*] Creating Linux desktop shortcut...")
        desktop_path = Path.home() / "Desktop"
        if not desktop_path.exists():
            desktop_path = Path.home() / "Desktop"  # Try alternative
            if not desktop_path.exists():
                print("[!] Could not find desktop directory")
                return
        
        shortcut_path = desktop_path / f"Launch_{avd_name}.desktop"
        emulator_path = find_executable(sdk_root / "emulator", "emulator")
        if not emulator_path:
            print("[!] Emulator not found")
            return
        
        content = f"""[Desktop Entry]
                        Version=1.0
                        Type=Application
                        Terminal=false
                        Exec={emulator_path} -avd {avd_name}
                        Name=Launch {avd_name}
                        Icon=android
                        """
        try:
            with open(shortcut_path, "w") as f:
                f.write(content)
            
            # Make executable
            shortcut_path.chmod(shortcut_path.stat().st_mode | stat.S_IEXEC)
            print(f"[+] Created desktop shortcut at {shortcut_path}")
        except Exception as e:
            print(f"[!] Failed to create shortcut: {e}")
        return
        
    # Windows shortcut creation
    install_pywin32_if_missing()
    try:
        import pythoncom
        from win32com.shell import shell, shellcon
        from win32com.client import Dispatch
    except ImportError:
        print("[!] pywin32 import failed. Skipping shortcut creation.")
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

    try:
        shell_obj = Dispatch('WScript.Shell')
        shortcut = shell_obj.CreateShortcut(shortcut_path)
        shortcut.TargetPath = str(target)
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = str(working_dir)
        shortcut.IconLocation = icon
        shortcut.Save()
        print(f"[+] Desktop shortcut created at: {shortcut_path}")
    except Exception as e:
        print(f"[!] Failed to create shortcut: {e}")

def create_avd_name(system_image):
    parts = system_image.split(";")
    android_version = parts[1].replace("android-", "API_")
    return f"Pixel{android_version}"

def check_dependencies():
    """Check for required dependencies"""
    missing = []
    
    # Platform-agnostic dependencies
    if not shutil.which("zip"):
        missing.append("zip")
    
    # Platform-specific dependencies
    if is_windows():
        pass  # Windows doesn't need additional tools
    else:
        if not shutil.which("unzip"):
            missing.append("unzip")
        if not shutil.which("java"):
            missing.append("java")
    
    if missing:
        print(f"[!] Missing required tools: {', '.join(missing)}")
        if not is_windows():
            print("On Ubuntu/Debian, try: sudo apt install unzip openjdk-11-jdk")
        return False
    return True

def prompt_gui():
    def on_install():
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select a system image to install.")
            return
        selected_image = listbox.get(selected_indices[0])
        root.selected_image = selected_image  # Same as original
        root.destroy()

    root = tk.Tk()
    root.title("System Image Selector")
    
    # Larger window
    root.geometry("750x550")
    
    # Modern fonts
    custom_font = ("Segoe UI", 12)  # Cleaner than Arial
    button_font = ("Segoe UI", 12, "bold")
    
    # Main frame for padding
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Listbox with scrollbar
    list_frame = tk.Frame(main_frame)
    list_frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox = tk.Listbox(
        list_frame,
        yscrollcommand=scrollbar.set,
        font=custom_font,
        height=15,
        width=70,
        bg="white",
        selectbackground="#0066CC"  # Blue selection
    )
    listbox.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)
    
    # Populate list (original logic)
    images = get_available_system_images()
    if not images:
        messagebox.showerror("Error", "No system images found.")
        root.destroy()
        return None
    
    for img in images:
        listbox.insert(tk.END, img)
    
    # Styled install button
    install_button = tk.Button(
        main_frame,
        text="Install",
        command=on_install,
        font=button_font,
        bg="#4CAF50",  # Green
        fg="white",
        padx=20,
        pady=5,
        relief=tk.FLAT,
        borderwidth=0
    )
    install_button.pack(pady=15)
    
    root.mainloop()
    
    # Preserve original return logic
    return getattr(root, "selected_image", None)

def download_progress_hook(block_count, block_size, total_size):
    """Display download progress with percentage"""
    downloaded = block_count * block_size
    if total_size > 0:
        percent = min(100, (downloaded * 100) // total_size)
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        
        # Print progress on same line - clean format without hash symbols
        print(f"\rDownloading... {percent}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='', flush=True)
    else:
        downloaded_mb = downloaded / (1024 * 1024)
        print(f"\rDownloaded: {downloaded_mb:.1f} MB", end='', flush=True)

def get_jdk_download_url():
    """Get the appropriate JDK 21 LTS download URL based on platform"""
    if is_windows():
        return "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.zip"
    else:
        return "https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.tar.gz"

def download_jdk():
    """Download JDK 21 LTS"""
    print("[*] Downloading JDK 21 LTS...")
    jdk_url = get_jdk_download_url()
    
    if is_windows():
        temp_dir = Path(tempfile.gettempdir())
        jdk_archive = temp_dir / "jdk21.zip"
    else:
        # Use user's home directory instead of system temp directory on Linux
        download_dir = Path.home() / "Downloads"
        download_dir.mkdir(exist_ok=True)
        jdk_archive = download_dir / "jdk21.tar.gz"
    
    try:
        urllib.request.urlretrieve(jdk_url, jdk_archive, download_progress_hook)
        print("\n[+] JDK download complete")
        return jdk_archive
    except Exception as e:
        print(f"\n[!] JDK download failed: {e}")
        return None

def extract_jdk(jdk_archive):
    """Extract JDK to the appropriate location"""
    if not jdk_archive or not jdk_archive.exists():
        return None
    
    print("[*] Extracting JDK...")
    
    # Install to user directory by default to avoid permission issues
    if not is_windows():
        jdk_dir = Path.home() / "jdk-21"
        if jdk_dir.exists():
            shutil.rmtree(jdk_dir)
        jdk_dir.mkdir(parents=True, exist_ok=True)
        print("[*] Installing JDK to user directory ~/jdk-21")
    else:
        jdk_dir = Path.home() / "jdk-21"
    
    try:
        if is_windows():
            with zipfile.ZipFile(jdk_archive, 'r') as zip_ref:
                zip_ref.extractall(jdk_dir)
        else:
            import tarfile
            with tarfile.open(jdk_archive, 'r:gz') as tar_ref:
                tar_ref.extractall(jdk_dir)
        
        # Find the actual JDK directory (it might be nested)
        jdk_home = None
        for item in jdk_dir.iterdir():
            if item.is_dir() and "jdk" in item.name.lower():
                jdk_home = item
                break
        
        if not jdk_home:
            print("[!] Could not find JDK directory after extraction")
            return None
        
        print(f"[+] JDK extracted to {jdk_home}")
        return jdk_home
    except Exception as e:
        print(f"[!] JDK extraction failed: {e}")
        return None

def set_java_env_vars(jdk_home):
    """Set JAVA_HOME and add Java to PATH"""
    if not jdk_home or not jdk_home.exists():
        return False
    
    print("[*] Setting Java environment variables...")
    
    if is_windows():
        try:
            import winreg
            # Set JAVA_HOME
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                               0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "JAVA_HOME", 0, winreg.REG_EXPAND_SZ, str(jdk_home))
                print("[+] JAVA_HOME set in Windows registry")
            
            # Update PATH
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                               0, winreg.KEY_ALL_ACCESS) as key:
                current_path, _ = winreg.QueryValueEx(key, "Path")
                path_parts = current_path.split(";")
                
                java_bin = str(jdk_home / "bin")
                if java_bin not in path_parts:
                    path_parts.append(java_bin)
                    new_path = ";".join(path_parts)
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    print("[+] Java added to PATH in Windows registry")
        except Exception as e:
            print(f"[!] Failed to update Windows registry: {e}")
            return False
    else:
        # Linux - determine if system-wide or user installation
        is_system_wide = str(jdk_home).startswith('/opt/')
        
        # Use current user's home directory
        user_home = Path.home()
        print("[*] Setting Java environment variables for current user")
        
        if is_system_wide:
            print("[*] System-wide Java installation detected")
        else:
            print("[*] User-specific Java installation detected")
        
        shell_configs = [
            user_home / ".bashrc",
            user_home / ".zshrc", 
            user_home / ".profile"
        ]
        
        export_lines = [
            f"export JAVA_HOME={jdk_home}",
            f"export PATH=$JAVA_HOME/bin:$PATH"
        ]
        
        # Set environment variables in current session
        os.environ['JAVA_HOME'] = str(jdk_home)
        current_path = os.environ.get('PATH', '')
        java_bin_path = str(jdk_home / "bin")
        if java_bin_path not in current_path:
            os.environ['PATH'] = f"{java_bin_path}:{current_path}"
        
        updated = False
        for config_file in shell_configs:
            if config_file.exists():
                try:
                    with open(config_file, 'r+') as f:
                        content = f.read()
                        needs_update = any(export not in content for export in export_lines)
                        
                        if needs_update:
                            f.write("\n# Java environment variables\n" + "\n".join(export_lines) + "\n")
                            print(f"[+] Updated {config_file} with Java paths")
                            updated = True
                except Exception as e:
                    print(f"[!] Failed to update {config_file}: {e}")
        
        if updated:
            print("[!] Please restart your terminal or run 'source ~/.bashrc' (or your shell config)")
    
    return True

def verify_java_installation(jdk_home):
    """Verify that Java is properly installed and working"""
    print("[*] Verifying Java installation...")
    
    # Check if java executable exists
    java_exe = jdk_home / "bin" / ("java.exe" if is_windows() else "java")
    if not java_exe.exists():
        print(f"[!] Java executable not found at {java_exe}")
        return False
    
    # Make executable on Linux
    if not is_windows():
        try:
            java_exe.chmod(java_exe.stat().st_mode | stat.S_IEXEC)
        except Exception as e:
            print(f"[!] Failed to make Java executable: {e}")
            return False
    
    # Test Java version
    try:
        result = subprocess.run([str(java_exe), "-version"], 
                              capture_output=True, 
                              text=True)
        if "version \"21" not in result.stderr:
            print("[!] Java version check failed")
            return False
        print("[+] Java version verified")
        
        # Test Java compiler
        javac_exe = jdk_home / "bin" / ("javac.exe" if is_windows() else "javac")
        if not javac_exe.exists():
            print(f"[!] Java compiler not found at {javac_exe}")
            return False
            
        result = subprocess.run([str(javac_exe), "-version"], 
                              capture_output=True, 
                              text=True)
        if "javac 21" not in result.stdout:
            print("[!] Java compiler version check failed")
            return False
        print("[+] Java compiler verified")
        
        return True
    except Exception as e:
        print(f"[!] Java verification failed: {e}")
        return False

def setup_jdk():
    """Main function to setup JDK 21 LTS"""
    print("\n== Setting up JDK 21 LTS ==")
    
    # Check if Java is already installed
    jdk_home = None
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        if "version \"21" in result.stderr:
            print("[+] JDK 21 is already installed")
            # Find the JDK installation directory
            if is_windows():
                jdk_home = Path.home() / "jdk-21"
            else:
                # Check user location first
                user_jdk = Path.home() / "jdk-21"
                if user_jdk.exists():
                    # Find the actual JDK directory
                    for item in user_jdk.iterdir():
                        if item.is_dir() and "jdk" in item.name.lower():
                            jdk_home = item
                            break
                else:
                    # Check system-wide location as fallback
                    system_jdk = Path("/opt/jdk-21")
                    if system_jdk.exists():
                        # Find the actual JDK directory
                        for item in system_jdk.iterdir():
                            if item.is_dir() and "jdk" in item.name.lower():
                                jdk_home = item
                                break
                    
                    if not jdk_home:
                        print("[!] JDK is installed but installation directory not found")
                        return False
    except:
        pass
    
    # If JDK is not installed, download and install it
    if not jdk_home:
        # Download and extract JDK
        jdk_archive = download_jdk()
        if not jdk_archive:
            return False
        
        jdk_home = extract_jdk(jdk_archive)
        if not jdk_home:
            return False
        
        # Clean up
        try:
            jdk_archive.unlink()
        except:
            pass
    
    # Verify installation
    if not verify_java_installation(jdk_home):
        print("[!] Java installation verification failed")
        return False
    
    # Set environment variables
    if not set_java_env_vars(jdk_home):
        return False
    
    # Clean up
    try:
        jdk_archive.unlink()
    except:
        pass
    
    print("[+] JDK 21 LTS setup complete")
    return True

def get_nodejs_download_url():
    """Get the appropriate Node.js 22 LTS download URL based on platform"""
    if is_windows():
        return "https://nodejs.org/dist/v22.0.0/node-v22.0.0-x64.msi"
    else:
        return "https://nodejs.org/dist/v22.0.0/node-v22.0.0-linux-x64.tar.xz"

def download_nodejs():
    """Download Node.js 22 LTS"""
    print("[*] Downloading Node.js 22 LTS...")
    node_url = get_nodejs_download_url()
    
    if is_windows():
        temp_dir = Path(tempfile.gettempdir())
        node_archive = temp_dir / "nodejs.msi"
    else:
        # Use user's home directory instead of system temp directory on Linux
        download_dir = Path.home() / "Downloads"
        download_dir.mkdir(exist_ok=True)
        node_archive = download_dir / "nodejs.tar.xz"
    
    try:
        urllib.request.urlretrieve(node_url, node_archive, download_progress_hook)
        print("\n[+] Node.js download complete")
        return node_archive
    except Exception as e:
        print(f"\n[!] Node.js download failed: {e}")
        return None

def install_nodejs(node_archive):
    """Install Node.js based on platform"""
    if not node_archive or not node_archive.exists():
        return False
    
    print("[*] Installing Node.js...")
    try:
        if is_windows():
            # Windows - use msiexec to install MSI
            subprocess.run(["msiexec", "/i", str(node_archive), "/quiet", "/norestart"], check=True)
            node_dir = Path("C:\\Program Files\\nodejs")
        else:
            # Linux - extract to a dedicated nodejs directory
            import tarfile
            
            # Clean up old broken symlinks in /usr/local/bin first
            print("[*] Cleaning up old Node.js symlinks...")
            usr_bin = Path("/usr/local/bin")
            for binary in ["node", "npm", "npx"]:
                old_link = usr_bin / binary
                if old_link.exists() or old_link.is_symlink():
                    try:
                        old_link.unlink()
                        print(f"[+] Removed old {binary} symlink")
                    except Exception as e:
                        print(f"[!] Could not remove {old_link}: {e}")
            
            # Install to user directory by default to avoid permission issues
            node_install_dir = Path.home() / "nodejs"
            if node_install_dir.exists():
                shutil.rmtree(node_install_dir)
            node_install_dir.mkdir(parents=True, exist_ok=True)
            print("[*] Installing Node.js to user directory ~/nodejs")
            
            # Extract to temp directory
            if is_windows():
                temp_extract_dir = Path(tempfile.gettempdir()) / "nodejs_extract"
            else:
                # Use user's home directory instead of system temp directory on Linux
                temp_extract_dir = Path.home() / "temp_nodejs_extract"
            
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
            temp_extract_dir.mkdir(parents=True, exist_ok=True)
            
            with tarfile.open(node_archive, 'r:xz') as tar_ref:
                tar_ref.extractall(temp_extract_dir)
            
            # Find extracted directory
            extracted_dir = temp_extract_dir / "node-v22.0.0-linux-x64"
            if not extracted_dir.exists():
                dirs = list(temp_extract_dir.glob("node-*"))
                if dirs:
                    extracted_dir = dirs[0]
                else:
                    print("[!] Could not find extracted Node.js directory")
                    return None
            
            # Move entire directory structure to preserve npm integrity
            for item in extracted_dir.iterdir():
                shutil.move(str(item), str(node_install_dir))
            
            # Clean up
            shutil.rmtree(temp_extract_dir)
            
            # Create symlinks in user bin directory
            user_bin = Path.home() / "bin"
            user_bin.mkdir(exist_ok=True)
            
            for binary in ["node", "npm", "npx"]:
                binary_path = node_install_dir / "bin" / binary
                symlink_path = user_bin / binary
                
                if binary_path.exists():
                    # Make executable
                    binary_path.chmod(binary_path.stat().st_mode | stat.S_IEXEC)
                    
                    # Remove old symlink if exists
                    if symlink_path.exists() or symlink_path.is_symlink():
                        try:
                            symlink_path.unlink()
                        except Exception as e:
                            print(f"[!] Could not remove old symlink {symlink_path}: {e}")
                    
                    # Create symlink
                    try:
                        symlink_path.symlink_to(binary_path)
                        print(f"[+] Created user symlink: {symlink_path} -> {binary_path}")
                    except Exception as e:
                        print(f"[!] Could not create user symlink {symlink_path}: {e}")
            
            print(f"[!] Please add {user_bin} to your PATH manually:")
            print(f"    echo 'export PATH={user_bin}:$PATH' >> ~/.bashrc")
            
            node_dir = node_install_dir
        
        print(f"[+] Node.js installed to {node_dir}")
        return node_dir
    except Exception as e:
        print(f"[!] Node.js installation failed: {e}")
        return None

def set_nodejs_env_vars(node_dir):
    """Set Node.js environment variables"""
    if not node_dir or not node_dir.exists():
        return False
    
    print("[*] Setting Node.js environment variables...")
    
    if is_windows():
        try:
            import winreg
            # Set NVM_HOME
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                               0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "NVM_HOME", 0, winreg.REG_EXPAND_SZ, str(node_dir))
                print("[+] NVM_HOME set in Windows registry")
            
            # Update PATH
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                               0, winreg.KEY_ALL_ACCESS) as key:
                current_path, _ = winreg.QueryValueEx(key, "Path")
                path_parts = current_path.split(";")
                
                # Add the main Node.js directory to PATH
                if str(node_dir) not in path_parts:
                    path_parts.append(str(node_dir))
                    new_path = ";".join(path_parts)
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    print("[+] Node.js added to PATH in Windows registry")
            
            # Refresh environment variables
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            SMTO_ABORTIFHUNG = 0x0002
            result = ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment",
                SMTO_ABORTIFHUNG, 5000, None
            )
            print("[+] Environment variables refreshed")
            
        except Exception as e:
            print(f"[!] Failed to update Windows registry: {e}")
            return False
    else:
        # Linux - update shell configuration files
        # Use current user's home directory
        user_home = Path.home()
        print("[*] Setting Node.js environment variables for current user")
        
        shell_configs = [
            user_home / ".bashrc",
            user_home / ".zshrc",
            user_home / ".profile"
        ]
        
        export_lines = [
            f"export NODE_HOME={node_dir}",
            f"export PATH=$NODE_HOME/bin:$PATH"
        ]
        
        # Set environment variables in current session
        os.environ['NODE_HOME'] = str(node_dir)
        current_path = os.environ.get('PATH', '')
        node_bin_path = str(node_dir / "bin")
        if node_bin_path not in current_path:
            os.environ['PATH'] = f"{node_bin_path}:{current_path}"
        
        updated = False
        for config_file in shell_configs:
            if config_file.exists():
                try:
                    with open(config_file, 'r+') as f:
                        content = f.read()
                        needs_update = any(export not in content for export in export_lines)
                        
                        if needs_update:
                            f.write("\n# Node.js environment variables\n" + "\n".join(export_lines) + "\n")
                            print(f"[+] Updated {config_file} with Node.js paths")
                            updated = True
                except Exception as e:
                    print(f"[!] Failed to update {config_file}: {e}")
        
        if updated:
            print("[!] Please restart your terminal or run 'source ~/.bashrc' (or your shell config)")
    
    return True

def verify_nodejs_installation(node_dir):
    """Verify that Node.js is properly installed and working"""
    print("[*] Verifying Node.js installation...")
    
    # Check if node executable exists
    node_exe = node_dir / "node.exe" if is_windows() else node_dir / "bin" / "node"
    if not node_exe.exists():
        print(f"[!] Node.js executable not found at {node_exe}")
        return False
    
    # Test Node.js version
    try:
        result = subprocess.run([str(node_exe), "--version"], 
                              capture_output=True, 
                              text=True)
        if "v22" not in result.stdout:
            print("[!] Node.js version check failed")
            return False
        print("[+] Node.js version verified")
        
        # Test npm
        npm_exe = node_dir / "npm.cmd" if is_windows() else node_dir / "bin" / "npm"
        if not npm_exe.exists():
            print(f"[!] npm not found at {npm_exe}")
            return False
            
        result = subprocess.run([str(npm_exe), "--version"], 
                              capture_output=True, 
                              text=True)
        print(f"[+] npm version: {result.stdout.strip()}")
        
        return True
    except Exception as e:
        print(f"[!] Node.js verification failed: {e}")
        return False

def setup_nodejs():
    """Main function to setup Node.js 22 LTS"""
    print("\n== Setting up Node.js 22 LTS ==")
    
    # Check if Node.js is already installed
    node_dir = None
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if "v22" in result.stdout:
            print("[+] Node.js 22 is already installed")
            # Find the Node.js installation directory
            if is_windows():
                node_dir = Path("C:\\Program Files\\nodejs")
            else:
                # Check user location first (preferred for non-sudo installations)
                user_node = Path.home() / "nodejs"
                if user_node.exists():
                    node_dir = user_node
                else:
                    # Check system-wide location as fallback
                    system_node = Path("/opt/nodejs")
                    if system_node.exists():
                        node_dir = system_node
                    else:
                        print("[!] Node.js is installed but installation directory not found")
                        return False
    except:
        pass
    
    # If Node.js is not installed, download and install it
    if not node_dir:
        # Download and install Node.js
        node_archive = download_nodejs()
        if not node_archive:
            return False
        
        node_dir = install_nodejs(node_archive)
        if not node_dir:
            return False
        
        # Clean up
        try:
            node_archive.unlink()
        except:
            pass
    
    # Verify installation
    if not verify_nodejs_installation(node_dir):
        print("[!] Node.js installation verification failed")
        return False
    
    # Set environment variables
    if not set_nodejs_env_vars(node_dir):
        return False
    
    # Clean up
    try:
        node_archive.unlink()
    except:
        pass
    
    print("[+] Node.js 22 LTS setup complete")
    return True

def install_appium():
    """Install Appium using npm"""
    print("\n== Installing Appium ==")
    
    # Check if Appium is already installed
    try:
        run(["appium", "--version"])
        print("[+] Appium is already installed")
        return True
    except:
        pass
    
    print("[*] Installing Appium...")
    try:
        # Find npm executable (use full path to avoid issues with broken symlinks)
        if is_windows():
            npm_path = Path("C:\\Program Files\\nodejs\\npm.cmd")
        else:
            # Try the new installation first
            npm_path = Path("/opt/nodejs/bin/npm")
            if not npm_path.exists():
                # Fall back to system npm
                npm_path = "npm"
            else:
                npm_path = str(npm_path)
        
        # Install Appium globally
        run([npm_path, "install", "-g", "appium"])
        print("[+] Appium installed successfully")
        
        # Install Appium Doctor for environment verification
        run([npm_path, "install", "-g", "appium-doctor"])
        print("[+] Appium Doctor installed successfully")
        
        # Run Appium Doctor to verify environment
        print("[*] Running Appium Doctor to verify environment...")
        
        # Try different ways to find appium-doctor
        appium_doctor_paths = [
            "/opt/nodejs/bin/appium-doctor",
            "/usr/local/bin/appium-doctor",
            "appium-doctor"
        ]
        
        appium_doctor_found = False
        for path in appium_doctor_paths:
            try:
                if Path(path).exists() or path == "appium-doctor":
                    run([path])
                    appium_doctor_found = True
                    break
            except:
                continue
        
        # Try using npx as fallback
        if not appium_doctor_found:
            try:
                print("[*] Trying to run appium-doctor with npx...")
                run(["npx", "appium-doctor"])
                appium_doctor_found = True
            except:
                pass
        
        if not appium_doctor_found:
            print("[!] Could not find appium-doctor executable")
            print("[*] Appium Doctor was installed but not found in PATH")
            print("[*] You can run it manually later with: npx appium-doctor")
            print("[+] Appium installation completed (without doctor verification)")
        
        return True
    except Exception as e:
        print(f"[!] Unexpected error during Appium installation: {e}")
        return False

def main():
    print("== Android Emulator Manager ==")
    print(f"Running on {platform.system()}")
    
    # Check for admin/root privileges - require on Windows, optional on Linux
    if not is_admin():
        if is_windows():
            print("[!] This script requires administrator privileges on Windows to:")
            print("    - Install JDK and Node.js")
            print("    - Set system environment variables")
            print("    - Install Android SDK components")
            run_as_admin()
            return
        else:
            print("[+] Running in user mode on Linux")
            print("[*] All components will be installed to user directories:")
            print("    - JDK: ~/jdk-21")
            print("    - Node.js: ~/nodejs")
            print("    - Android SDK: ~/Android/Sdk")
    else:
        print("[+] Running with administrator/root privileges")

    # Setup JDK first
    if not setup_jdk():
        print("[!] JDK setup failed. Exiting.")
        sys.exit(1)

    # Setup Node.js
    if not setup_nodejs():
        print("[!] Node.js setup failed. Exiting.")
        sys.exit(1)

    # Install Appium
    if not install_appium():
        print("[!] Appium installation failed. Exiting.")
        sys.exit(1)

    # if not check_dependencies():
    #     sys.exit(1)

    ensure_dirs()
    download_cmdline_tools()
    extract_cmdline_tools()
    set_env_vars()

    action = prompt_gui()
    if not action:
        print("[!] No action selected. Exiting.")
        return

    if action.startswith("RUN_"):
        avd_name = action[4:]
        run_emulator(avd_name)
    else:
        system_image = action
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