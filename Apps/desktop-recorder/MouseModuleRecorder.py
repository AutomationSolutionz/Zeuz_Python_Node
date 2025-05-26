import time
import pickle
import sys
import mouse
from pathlib import Path


class MouseModuleRecorder:
    def __init__(self):
        """
        Metadata for the events to be stored/transferred for later playback.

        Keys:
        version: Information for checking compatibility with future versions
          of recordings.
        platform: Current os/platform in which this was recorded.
        type: Indicates the backend used for recording. In future, we may have
          multiple backends which support both mouse and keyboard recording
          with different modules.
        """
        self.recording_data = {
            "recorder_type": "mousemodule",
            "version": 1,
            "platform": sys.platform,
            "events": []
        }


    def decide_next_filename(self):
        globs = Path(".").glob("recording_*")
        recording_files = [f for f in globs if f.is_file()]
        n = 0
        for f in recording_files:
            num = int(f.stem.split("_")[1])
            n = max(num, n)

        name = "recording_%d.zvt" % (n + 1)
        return name


    def record(self):
        print("Starting recording in 3 sec...")
        print("Press MIDDLE MOUSE button to stop recording.")
        time.sleep(3)
        print("Started recording...")
        recorded = mouse.record(button=mouse.MIDDLE, target_types=(mouse.UP,))
        mouse.unhook_all()
        print("DONE")

        self.recording_data["events"] = recorded
        self.store_recordings(self.recording_data)


    def store_recordings(self, data):
        name = self.decide_next_filename()
        print("Saving as: %s" % name)
        with open(name, "wb") as f:
            pickle.dump(data, f)


def main():
    recorder = MouseModuleRecorder()
    recorder.record()


if __name__ == "__main__":
    main()
