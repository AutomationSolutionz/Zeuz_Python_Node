import pickle
from typing import Dict, Any
from Framework.Built_In_Automation.Desktop.RecordPlayback.MouseModulePlayback import MouseModulePlayback


"""
Metadata for the events to be stored/transferred for later playback.

Keys:
version: Information for checking compatibility with future versions
    of recordings.
platform: Current os/platform in which this was recorded.
type: Indicates the backend used for recording. In future, we may have
    multiple backends which support both mouse and keyboard recording
    with different modules.

recording_data = {
    "recorder_type": "mousemodule",
    "version": 1,
    "platform": sys.platform,
    "events": []
}
"""


def load_recording_data_from_file(filepath) -> Dict[str, Any]:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
            return data


class ChoosePlaybackModule:
    def __init__(self, filepath) -> None:
        self.data = None
        self.playback_class = self.choose(filepath=filepath)


    def choose(self, filepath) -> MouseModulePlayback:
        """
        choose will automatically pick the playback module to use based on the
        recorder type specified in the loaded data. In future, this will may also
        check for version and platform compatibility.
        """
        self.data = load_recording_data_from_file(filepath)
        if self.data["recorder_type"] == "mousemodule":
            return MouseModulePlayback


    def play(self, speed_factor):
        playback = self.playback_class(self.data)
        playback.play(speed_factor=speed_factor)
