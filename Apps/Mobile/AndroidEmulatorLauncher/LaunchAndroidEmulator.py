import os
import sys
import subprocess


def get_sdk_path():
    """
    Dynamically retrieve the Android SDK path from environment variables or default locations.
    """
    # Check if ANDROID_HOME or ANDROID_SDK_ROOT is set
    sdk_path = os.getenv("ANDROID_HOME") or os.getenv("ANDROID_SDK_ROOT")

    if not sdk_path:
        # Fallback to default installation paths
        default_paths = [
            os.path.expanduser(r"~\AppData\Local\Android\Sdk"),  # Windows
            os.path.expanduser("~/Library/Android/sdk"),  # macOS
            os.path.expanduser("~/.android/sdk"),  # Linux
        ]
        for path in default_paths:
            if os.path.exists(path):
                sdk_path = path
                break

    if not sdk_path or not os.path.exists(sdk_path):
        sys.exit(
            "Android SDK path not found. Please set ANDROID_HOME or ANDROID_SDK_ROOT."
        )

    return sdk_path


def get_emulator_path():
    """
    Construct the path to the emulator executable based on the SDK path.
    """
    sdk_path = get_sdk_path()
    emulator_path = os.path.join(
        sdk_path, "emulator", "emulator.exe" if os.name == "nt" else "emulator"
    )

    if not os.path.exists(emulator_path):
        sys.exit(f"Emulator executable not found at: {emulator_path}")

    return emulator_path


def get_avds(emulator_path):
    """
    Retrieve the list of available Android Virtual Devices (AVDs).
    """
    try:
        result = subprocess.run(
            [emulator_path, "-list-avds"], capture_output=True, text=True, check=True
        )
        avds = result.stdout.strip().splitlines()
        return avds if avds else []
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving AVDs: {e}")
        return []


def display_menu(options):
    """
    Display a selection menu for the user without external modules.
    """
    print("\nSelect an emulator to launch:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = int(input("\nEnter your choice (number): ")) - 1
            if 0 <= choice < len(options):
                return options[choice]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def launch_avd(emulator_path, avd_name):
    """
    Launch the selected Android Virtual Device (AVD).
    """
    print(f"\nLaunching emulator: {avd_name}...")
    try:
        subprocess.run([emulator_path, "-avd", avd_name], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(f"Failed to start emulator: {avd_name}. Error: {e}")


def main():
    """
    Main function to list and launch AVDs.
    """
    # Get the path to the emulator executable
    emulator_path = get_emulator_path()

    # Retrieve the list of available AVDs
    avds = get_avds(emulator_path)

    if not avds:
        sys.exit(
            "No Android Virtual Devices found. Please create one using AVD Manager."
        )

    # Display the menu and let the user select an AVD
    avd_name = display_menu(avds)

    # Launch the selected AVD
    launch_avd(emulator_path, avd_name)


if __name__ == "__main__":
    main()
