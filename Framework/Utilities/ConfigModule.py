# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
from filelock import FileLock
import configparser, os, threading
from . import FileUtilities as FL
from pathlib import Path
from datetime import date
from configobj import ConfigObj
import traceback

"""constants"""
file_name = "settings.conf"
settings_file_lock = FileLock(os.getcwd().split("Framework")[0] + os.sep + "Framework" + os.sep + file_name + ".lock")
settings_conf_path = os.getcwd().split("Framework")[0] + os.sep + "Framework" + os.sep + file_name
remote_config = {
    "threading": False,
    "local_run": False,
    "take_screenshot": True,
    "debug_mode": False,
    "upload_log_file_only_for_fail": True,
}

# Parsed config files, reused while the file on disk is unchanged. Config values
# are read many times per log line, and re-reading the file under the file lock
# every time made logging very slow. Every write in this module clears the cache;
# the file signature catches changes made by other processes.
_config_cache = {}  # absolute path -> (file signature, ConfigParser)
_config_cache_lock = threading.Lock()


def _file_signature(path):
    try:
        st = os.stat(path)
    except OSError:
        return None
    return (st.st_mtime_ns, st.st_size, st.st_ino)


def _clear_config_cache():
    with _config_cache_lock:
        _config_cache.clear()


def _read_config(_file_name, location):
    """Return the parsed config file, from the cache when the file is unchanged."""
    path = os.path.abspath(os.fspath(_file_name))
    signature = _file_signature(path)
    if signature is not None:
        with _config_cache_lock:
            cached = _config_cache.get(path)
        if cached is not None and cached[0] == signature:
            return cached[1]

    with settings_file_lock:
        # Taken before reading: if the file changes while it is read, the next
        # call sees a different signature and reads it again.
        signature = _file_signature(path)
        config = configparser.ConfigParser()
        config.optionxform = str  # Retain text case (default is to change to lowercase without this line)
        try:
            config.read(_file_name)  # Read current configuration, if the file exists
        except Exception:
            FL.DeleteFile(location)
            config.read(_file_name)
            signature = None  # the file was replaced; don't cache this read
        if signature is not None:
            with _config_cache_lock:
                _config_cache[path] = (signature, config)
    return config

@settings_file_lock
def create_settings_config_file():
    if Path(settings_conf_path).exists():
        return

    today = date.today().strftime("%Y-%m-%d")

    config = ConfigObj()
    config["Authentication"] = {"username": "", "api-key": "", "server_address": ""}
    config["Advanced Options"] = {
        "log_delete_interval": 7,
        "last_module_update_date": today,
        "last_log_delete_date": today,
        "element_wait": 10,
        "available_to_all_project": False,
        "_file": "temp_config.ini",
        "_file_upload_path": "TestExecutionLog",
        "stop_live_log": False,
        "take_screenshot": "",
    }
    config["Inspector"] = {
        "Window": "",
        "No_of_level_to_skip": 0,
        "ai_plugin": True,
    }
    config["server"] = {"port": 0}
    config.filename = str(settings_conf_path)
    try:
        config.write()
    finally:
        _clear_config_cache()
    print(f"Created settings.conf at {settings_conf_path}")

def remove_settings_lock_file():
    """Remove stale lock file if the process that created it is no longer running."""
    try:
        lock_file_path = Path(settings_file_lock.lock_file)
        if not lock_file_path.exists():
            return
        lock_file_path.unlink(missing_ok=True)
    except Exception:
        traceback.print_exc()

def get_config_value(section, key, location: os.PathLike | None = None):
    """
    :param section: name of section
    :param key: name of key
    :return: value of the key in that section
    """
    try:
        global remote_config
        if section == "RunDefinition" and key in remote_config:
            return str(remote_config[key])

        if not location:
            _file_name = os.getcwd().split("Framework")[0] + os.sep + "Framework" + os.sep + file_name
        else:
            _file_name = location
        config = _read_config(_file_name, location)
        return config.get(section, key)
    except configparser.NoSectionError:
        # print "No section in that name: %s"%section
        return ""
    except configparser.NoOptionError:
        # print "No option in that name: %s"%key
        return ""

@settings_file_lock
def remove_config_value(section, value, location=False):
    try:
        config = configparser.ConfigParser()
        config.optionxform = str  # Retain text case (default is to change to lowercase without this line)
        if not location:
            _file_name = os.getcwd() + os.sep + file_name
        else:
            _file_name = location
        try:
            config.read(_file_name)  # Read current configuration, if the file exists
        except:
            FL.DeleteFile(location)
            config.read(_file_name)
        config.remove_option(section, value)
        with (open(_file_name, "w")) as open_file:
            config.write(open_file)
        open_file.close()
        return True
    except configparser.NoSectionError:
        # print "No section in that name: %s"%section
        return ""
    finally:
        _clear_config_cache()

@settings_file_lock
def add_config_value(section, key, value, location: os.PathLike | None = None):
    try:
        config = configparser.ConfigParser()
        config.optionxform = str  # Retain text case (default is to change to lowercase without this line)
        if not location:
            _file_name = os.getcwd() + os.sep + file_name
        else:
            _file_name = str(location)

        if os.path.exists(_file_name):
            try:
                config.read(
                    _file_name
                )  # Read current configuration, if the file exists
            except:
                FL.DeleteFile(location)
                config.read(_file_name)
        else:
            config.add_section(section)  # New file, so we have to add the section first
        if type(value) is bytes:
            print("In Bytes")
            config.set(
                section, key, value.decode()
            )  # Set new configuration from parameters

        else:
            config.set(section, key, value)

        with open(_file_name, "w") as open_file:
            config.write(open_file)  # Write all configuration to file
        open_file.close()
        return True
    except configparser.NoSectionError:
        return ""
    except configparser.NoOptionError:
        return ""
    finally:
        _clear_config_cache()


def add_section(section_name, location: os.PathLike | None = None):
    """
    :param section_name: name of the section to add
    :return: true or false
    """
    try:
        config = configparser.ConfigParser()
        config.optionxform = str  # Retain text case (default is to change to lowercase without this line)
        if not location:
            _file_name = os.getcwd() + os.sep + file_name
        else:
            _file_name = location
        try:
            config.read(_file_name)  # Read current configuration, if the file exists
        except:
            FL.DeleteFile(location)
            config.read(_file_name)
        config.add_section(section_name)
        with (open(_file_name, "w")) as open_file:
            config.write(open_file)
        open_file.close()
        return True
    except configparser.NoSectionError as e:
        print("Found no section with name %s" % section_name)
        return []
    except configparser.NoOptionError as e:
        print("Found no options on the section %s" % section_name)
        return []
    finally:
        _clear_config_cache()


def clean_config_file(location: os.PathLike | None = None):
    try:
        config = configparser.ConfigParser()
        config.optionxform = str  # Retain text case (default is to change to lowercase without this line)
        if not location:
            _file_name = os.getcwd() + os.sep + file_name
        else:
            _file_name = location
        get_all_section = config.sections()
        for each in get_all_section:
            config.remove_section(each)
        with (open(_file_name, "w")) as open_file:
            config.write(open_file)
        open_file.close()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        _clear_config_cache()
