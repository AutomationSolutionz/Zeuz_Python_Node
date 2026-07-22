#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-


import json
import shutil
import subprocess
import sys

from Framework.install_handler.android.android_sdk import get_adb_path

# These create the device name we give to each device
device_name = "device "
device_cnt = 1


def _get_adb_executable():
    """Prefer the ZeuZ-managed adb and fall back to a native adb on PATH."""
    managed_adb = get_adb_path()
    if managed_adb.is_file():
        return str(managed_adb)
    return shutil.which("adb")


def _adb_output(adb_executable, *args, timeout=30):
    return subprocess.check_output(
        [adb_executable, *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def get_all_connected_android_info():
    """For all connected Android devices, get specified information and return in a dictionary with the serial number as the top level key"""

    global device_cnt
    try:
        android_list = []
        device_list = {}

        adb_executable = _get_adb_executable()
        if not adb_executable:
            return {}

        # Get list of devices
        _adb_output(adb_executable, "start-server")
        result = _adb_output(adb_executable, "devices")
        for line in result.replace("\r", "").splitlines():
            fields = line.split()
            if len(fields) >= 2 and fields[1] == "device":
                android_list.append(fields[0])

        if len(android_list) == 0:
            return False
        # Get device information
        for serial in android_list:
            # Execute commands
            os_version = _adb_output(
                adb_executable,
                "-s",
                serial,
                "shell",
                "getprop",
                "ro.build.version.release",
            )
            model = _adb_output(
                adb_executable,
                "-s",
                serial,
                "shell",
                "getprop",
                "ro.product.model",
            )
            name = _adb_output(
                adb_executable,
                "-s",
                serial,
                "shell",
                "getprop",
                "ro.product.name",
            )
            mfg = _adb_output(
                adb_executable,
                "-s",
                serial,
                "shell",
                "getprop",
                "ro.product.manufacturer",
            )
            imei = _adb_output(
                adb_executable,
                "-s",
                serial,
                "shell",
                "dumpsys",
                "iphonesubinfo",
            )

            # Cleanup of results
            os_version = os_version.strip()
            model = model.strip()
            name = name.strip()
            mfg = mfg.strip()
            imei = imei.strip()
            if imei != "":
                imei = str(imei.split("\n")[-1]).strip()  # Last line should be IMEI
                imei = str(
                    imei.split(" ")[-1]
                ).strip()  # Last word on this line is IMEI
            else:  # Try alternative method to get imei
                imei = _adb_output(
                    adb_executable,
                    "-s",
                    serial,
                    "shell",
                    "service",
                    "call",
                    "iphonesubinfo",
                    "1",
                )
                imei = imei.split(" ")
                final = ""
                for line in imei:
                    if "'" in line:
                        final += line
                imei = (
                    final.replace("\r", "")
                    .replace("\n", "")
                    .replace("'", "")
                    .replace(".", "")
                    .replace(")", "")
                )  # Remove all unnecessary characters
                if len(imei) not in (14, 15, 18):
                    imei = "Unknown"

            # Compile information into dictionary
            dname = device_name + str(device_cnt)
            device_list[dname] = {}
            device_list[dname]["id"] = serial
            device_list[dname]["type"] = "Android"
            device_list[dname]["osver"] = os_version
            device_list[dname]["model"] = model
            device_list[dname]["devname"] = name
            device_list[dname]["mfg"] = mfg
            device_list[dname]["imei"] = imei
            device_cnt += 1

        return device_list
    except Exception as e:
        # CommonUtil.ExecLog('', 'Error reading Android device: %s' % e, 4, False)
        return {}


def get_all_connected_ios_info():
    """For all connected IOS devices, get specified information and return in a dictionary with the UUID as the top level key"""

    global device_cnt
    try:
        info_list = {}
        device_list = {}

        # Get list of UUIDs
        ios_list = subprocess.check_output(
            "idevice_id -l",
            shell=True,
            encoding="utf-8",
            # Suppress shell "command not found" noise (e.g. when libimobiledevice
            # is not installed, common on Android-only runs) from leaking to the
            # console.
            stderr=subprocess.DEVNULL,
        )
        ios_list = ios_list.split("\n")

        # Parse information for each device
        for uuid in ios_list:
            if uuid == "":
                continue
            info = ""
            try:
                info = subprocess.check_output(
                    "ideviceinfo -u %s" % uuid,
                    shell=True,
                    encoding="utf-8",
                    stderr=subprocess.DEVNULL,
                )
            except:
                pass
            if "ProductType" not in info:
                info = subprocess.check_output(
                    "ideviceinfo -s -u %s" % uuid,
                    shell=True,
                    encoding="utf-8",
                    stderr=subprocess.DEVNULL,
                )  # Try simple mode which gets everything we need except IMEI
            # info = info.encode('ascii', 'ignore') # !!!!Needed, but not working
            info = info.split("\n")

            # For each piece of information, add to a dictionary
            for line in info:
                key = line.split(" ")[0].replace(":", "")
                value = " ".join(line.split(" ")[1:])
                info_list[key] = value

            # Compile desired information into dictionary
            try:
                dname = device_name + str(device_cnt)
                device_list[dname] = {}
                device_list[dname]["id"] = uuid
                device_list[dname]["type"] = "IOS"
                device_list[dname]["mfg"] = "Apple"
                device_list[dname]["devname"] = info_list["DeviceName"]
                device_list[dname]["model"] = info_list["ProductType"]
                device_list[dname]["osver"] = info_list["ProductVersion"]
                try:
                    device_list[dname]["imei"] = info_list[
                        "InternationalMobileEquipmentIdentity"
                    ]
                except:
                    device_list[dname]["imei"] = "Unknown"
            except:  # Likely means we didn't get the info we needed
                pass
            device_cnt += 1

        return device_list
    except Exception as e:
        # CommonUtil.ExecLog('', 'Error reading IOS device: %s' % e, 4, False)
        return {}


def get_all_booted_ios_simulator_info():
    """For all booted simulator IOS devices, get specified information and return in a dictionary with the UUID as the top level key"""
    global device_cnt
    try:
        device_list = {}
        all_ios_simulators = subprocess.check_output(
            "xcrun simctl list --json", shell=True, encoding="utf-8"
        )
        data = json.loads(all_ios_simulators)
        for each in list(data["devices"].keys()):
            if "iOS" in each:
                splitted = str(each).split(" ")
                if len(splitted) > 1:
                    version = splitted[1]
                else:
                    version = each
                break

        for each_type in data["devices"]:
            all_ios_devices = data["devices"][each_type]
            # Compile desired information into dictionary
            for each in all_ios_devices:
                if each["state"] == "Booted":
                    try:
                        dname = device_name + str(device_cnt)
                        device_list[dname] = {}
                        device_list[dname]["id"] = each["udid"]
                        device_list[dname]["type"] = "IOS"
                        device_list[dname]["mfg"] = "Apple"
                        device_list[dname]["devname"] = each["name"]
                        device_list[dname]["model"] = each["name"]
                        device_list[dname]["osver"] = version
                        device_list[dname]["imei"] = "Simulated"
                    except:
                        pass

                    device_cnt += 1

        return device_list

    except Exception as e:
        # CommonUtil.ExecLog('', 'Error reading IOS device: %s' % e, 4, False)
        return {}


def get_all_connected_device_info():
    """For all connected IOS and Android devices, get specified information and return in a dictionary with the serial number/UUID as the top level key"""

    try:
        device_list = {}
        global device_cnt
        device_cnt = 1
        android_devices = get_all_connected_android_info()
        if android_devices:
            device_list = android_devices

        if sys.platform == "darwin":
            device_list.update(get_all_booted_ios_simulator_info())
            device_list.update(
                get_all_connected_ios_info()
            )  # Only run this when on Mac

        # return devices

        return device_list

    except Exception as e:  # Don't show any error because the user may not be running mobile automation
        # CommonUtil.ExecLog('', 'Error reading Android or IOS device: %s' % e, 4, False)
        return {}


if __name__ == "__main__":
    print(get_all_connected_device_info())
