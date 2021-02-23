# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import configparser, os
from . import FileUtilities as FL

"""constants"""
file_name = "settings.conf"

remote_config = {
    "threading": False,
    "local_run": False,
    "take_screenshot": True,
    "debug_mode": False,
    "upload_log_file_only_for_fail": True,
}


def get_config_value(section, key, location=False):
    """
    :param section: name of section
    :param key: name of key
    :return: value of the key in that section
    """
    try:
        global remote_config
        if key in remote_config:
            return str(remote_config[key])

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
        return config.get(section, key)
    except configparser.NoSectionError:
        # print "No section in that name: %s"%section
        return ""
    except configparser.NoOptionError:
        # print "No option in that name: %s"%key
        return ""


def remove_config_value(section, value, location=False):
    try:
        config = configparser.SafeConfigParser()
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


def add_config_value(section, key, value, location=False):
    try:
        config = configparser.ConfigParser()
        config.optionxform = str  # Retain text case (default is to change to lowercase without this line)
        if not location:
            _file_name = os.getcwd() + os.sep + file_name
        else:
            _file_name = location

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

        with (open(_file_name, "w")) as open_file:
            config.write(open_file)  # Write all configuration to file
        open_file.close()
        return True
    except configparser.NoSectionError:
        # print "No section in that name: %s"%section
        return ""
    except configparser.NoOptionError:
        # print "No option in that name: %s"%key
        return ""


def get_all_option(section_name, location=False):
    """
    :param section_name: given section name
    :return: list of all option on that section
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
        return config.options(section_name)
    except configparser.NoSectionError as e:
        # print("Found no section with name %s" % section_name)
        return []
    except configparser.NoOptionError as e:
        # print("Found no options on the section %s" % section_name)
        return []


def add_section(section_name, location=False):
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


def clean_config_file(location=False):
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


def get_all_sections(location=False):
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
        return config.sections()
    except configparser.NoSectionError as e:
        print("found no sections")
        return []
    except configparser.NoOptionError as e:
        print("found no options")
        return []

def has_section(section_name, location=False):
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
        return config.has_section(section_name)
    except configparser.NoSectionError as e:
        print("found no sections")
        return []
    except configparser.NoOptionError as e:
        print("found no options")
        return []