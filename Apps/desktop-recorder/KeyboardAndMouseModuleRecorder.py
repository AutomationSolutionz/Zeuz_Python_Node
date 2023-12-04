import sys
import time
import pickle
from pathlib import Path
from enum import Enum, auto
from threading import Thread
import datetime

import mouse
import keyboard


class EventType(Enum):
    MouseMove = auto()
    MouseUp = auto()
    MouseDown = auto()
    MouseWheel = auto()
    KeyDown = auto()
    KeyUp = auto()


class EventData:
    """
    Event Data, mouse or keyboard

    event_type: EventType, type of event that occurred
    timestamp: str, time when event occurred
    data: object, data of event

    """

    def __init__(self, event_type: EventType, timestamp: str, data: object):
        self.event_type = event_type
        self.timestamp = timestamp
        self.data = data

    def __repr__(self) -> str:
        return f"{self.timestamp}: {self.event_type}, {self.data}"


class KeyboardAndMouseModuleRecorder:

    def __init__(self) -> None:
        """
        Metadata for the events to be stored/transferred for later playback.

        Keys:
        version: Information for checking compatibility with future versions
          of recordings.
        platform: Current os/platform in which this was recorded.
        type: Indicates the backend used for recording. In the future, we may have
          multiple backends which support both mouse and keyboard recording
          with different modules.
        """
        self.recording_data = {
            "recorder_type": "mouseandkeyboardmodule",
            "version": 1,
            "platform": sys.platform,
            "events": []
        }

    def capture_mouse(self, event):
        timestamp = time.strftime("%H:%M:%S", time.localtime())

        if isinstance(event, mouse.MoveEvent):
            data = EventData(EventType.MouseMove, timestamp, event)
            self.recording_data["events"].append(data)
            # print(data)

        elif isinstance(event, mouse.ButtonEvent):
            if event.event_type == mouse.UP:
                data = EventData(EventType.MouseUp, timestamp, event)
                self.recording_data["events"].append(data)
            else:
                data = EventData(EventType.MouseDown, timestamp, event)
                self.recording_data["events"].append(data)
                # print(data)

        elif isinstance(event, mouse.WheelEvent):
            data = EventData(EventType.MouseWheel, timestamp, event)
            self.recording_data["events"].append(data)
            # print(data)

    def capture_keyboard(self, event):
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        if event.event_type == keyboard.KEY_UP:
            data = EventData(EventType.KeyUp, timestamp, event)
            self.recording_data["events"].append(data)
            # print(data)
        elif event.event_type == keyboard.KEY_DOWN:
            data = EventData(EventType.KeyDown, timestamp, event)
            self.recording_data["events"].append(data)
            # print(data)

    def decide_next_filename(self):
        globs = Path(".").glob("recording_*")
        recording_files = [f for f in globs if f.is_file()]
        recording_nums = [int(f.stem.split("_")[1]) for f in recording_files]
        max_name_num = 0 if len(recording_nums) == 0 else max(recording_nums)
        name = "recording_%d.zvt" % (max_name_num + 1)
        return name

    def save_data(self) -> None:
        name = self.decide_next_filename()
        print("Saving as: %s" % name)
        with open(name, "wb") as f:
            pickle.dump(self.recording_data, f)

    def replay(self,
               filename: str,
               type_delay: float = 0.05,
               mouse_click_delay: float = 0.05,
               mouse_move_delay: float = 0.002,
               mouse_scroll_delay: float = 0.01
               ) -> None:
        """
        filename: str, recorded file to load and replay
        type_delay: int, delay between each key press (speed of typing)
        mouse_click_delay: int, delay between each mouse click
        mouse_move_delay: int, control how slow the mouse moves
        mouse_scroll_delay: int, control how slow mouse scrolls
        """
        time.sleep(5)

        click_delay_in_between = 0.0005

        with open(filename, "rb") as f:
            self.recording_data = pickle.load(f)

        events = self.recording_data["events"]

        # print("Replaying...")
        prev_timestamp = None

        for event in events:
            if prev_timestamp is not None:
                current_time = datetime.datetime.strptime(event.timestamp, "%H:%M:%S")
                prev_time = datetime.datetime.strptime(prev_timestamp, "%H:%M:%S")
                time_diff = (current_time - prev_time).total_seconds()
                time.sleep(time_diff)

            if event.event_type == EventType.KeyUp or event.event_type == EventType.KeyDown:
                if event.data.event_type == keyboard.KEY_DOWN:
                    keyboard.press(event.data.name.lower())
                    time.sleep(type_delay)
                elif event.data.event_type == keyboard.KEY_UP:
                    keyboard.release(event.data.name.lower())
            else:
                data = event.data
                if isinstance(data, mouse.MoveEvent):
                    mouse.move(data.x, data.y)
                    time.sleep(mouse_move_delay)
                elif isinstance(data, mouse.ButtonEvent):
                    if data.event_type == mouse.UP:
                        mouse.press(data.button)
                        time.sleep(click_delay_in_between)  # constant click delay
                        mouse.release(data.button)
                        time.sleep(mouse_click_delay)

                elif isinstance(data, mouse.WheelEvent):
                    # Adjust mouse_scroll_delay to make scrolling slower
                    mouse.wheel(data.delta)
                    time.sleep(mouse_scroll_delay)

            prev_timestamp = event.timestamp

    def record(self):
        print("Starting recording in 3 sec...")
        print("Press MIDDLE MOUSE button to stop recording.")
        time.sleep(3)
        print("Started recording...")
        mouse_thread = Thread(target=lambda: mouse.hook(self.capture_mouse))
        keyboard_thread = Thread(target=lambda: keyboard.hook(self.capture_keyboard))

        mouse_thread.start()
        keyboard_thread.start()
        # print("Recording Started")
        # keyboard.wait(hotkey='ctrl+q') # keyboard option to stop recording
        mouse.wait(mouse.MIDDLE)
        print("DONE")

        self.save_data()
        mouse_thread.join()
        keyboard_thread.join()


if __name__ == "__main__":
    time.sleep(5)
    er = KeyboardAndMouseModuleRecorder()
    # er.record()
    er.replay("recording_1.zvt")
