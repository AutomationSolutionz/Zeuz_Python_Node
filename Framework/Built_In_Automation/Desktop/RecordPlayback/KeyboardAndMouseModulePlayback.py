import pickle
import time
import datetime

import keyboard
import mouse

from .commons import EventType


class KeyboardAndMouseModulePlayback:
    def __init__(self, data) -> None:
        self.data = data

    def play(self,
             speed_factor=1.0,
             type_delay: float = 0.05,
             mouse_click_delay: float = 0.05,
             mouse_move_delay: float = 0.002,
             mouse_scroll_delay: float = 0.01
             ) -> None:
        if not self.data:
            raise RuntimeError("`data` cannot be None")
        if "events" not in self.data:
            raise RuntimeError("`data['events']` cannot be None")

        time.sleep(5)

        click_delay_in_between = 0.0005

        events = self.data["events"]

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


def main():
    with open("recording_1.zvt", "rb") as f:
        data = pickle.load(f)
        playback = KeyboardAndMouseModulePlayback(data)
        playback.play(3.0)


if __name__ == "__main__":
    main()
