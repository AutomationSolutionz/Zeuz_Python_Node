from Framework.Utilities.All_Device_Info import get_all_connected_device_info


def get_local_run_info():
    return get_all_connected_device_info()

def get_device_info(device_selected):
    if(device_selected=='Local Machine'):
        return get_local_run_info()