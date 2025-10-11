# Android Development Setup - Quick Start


### Step 1: First Time Setup (Run Once)

**Run:** `AndroidSetup.py`

**What it does:**
- Installs JDK 21 LTS (~190 MB)
- Installs Node.js 22 LTS (~50 MB)
- Installs Appium (mobile automation)
- Installs Android SDK & Command Line Tools (~150 MB)
- Downloads your first Android system image (~500-800 MB)
- Creates your first Android Virtual Device (AVD)
- Creates desktop shortcut for the AVD


**Windows:**
```Terminal / powershell
python AndroidSetup.py
```

**Linux:**
```bash / terminal
sudo python3 AndroidSetup.py
```

---

### Step 2: Daily Usage (Run Anytime after running the step 1 file )

**Run:** `Avd_Launcher.py` 

**What it does:**
- Shows all installed Android emulators
- Launch existing emulators with one click
- Add new Android Virtual Devices
- Creates desktop shortcut to itself (first run only)

**Windows:**
```powershell
python Avd_Launcher.py
# Or double-click "Android AVD Launcher" desktop shortcut
```

**Linux:**
```bash
python3 Avd_Launcher.py
# Or double-click "Android_AVD_Launcher.desktop" shortcut
```

---

Note : The user only needs to follow the step 1 instuction once. 
For launching the avd launcher, the user can either follow the instruction of step 2 on how to run the file or just use the avd launcher desktop shortcut. 
