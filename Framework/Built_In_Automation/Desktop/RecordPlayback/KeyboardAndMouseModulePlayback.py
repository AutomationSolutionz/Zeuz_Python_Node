import pickle
import time

import keyboard
import mouse

from .commons import EventType


class KeyboardAndMouseModulePlayback:
    def __init__(self, data) -> None:
        self.data = data

    def play(self,
             speed_factor=1.0,
             type_delay: float = 0.05,
             mouse_click_delay: float = 0.03,
             mouse_move_delay: float = 0.001,
             mouse_scroll_delay: float = 0.01
             ) -> None:
        if not self.data:
            raise RuntimeError("`data` cannot be None")
        if "events" not in self.data:
            raise RuntimeError("`data['events']` cannot be None")

        events = self.data["events"]

        for event in events:
            if event.event_type == EventType.KeyUp or event.event_type == EventType.KeyDown:
                if event.data.event_type == keyboard.KEY_DOWN:
                    keyboard.press(event.data.name.lower())
                    time.sleep(type_delay)
                elif event.data.event_type == keyboard.KEY_UP:
                    keyboard.release(event.data.name.lower())
            else:
                data = event.data
                if isinstance(data, mouse.MoveEvent):
                    mouse.move(data.x, event.data.y)
                    time.sleep(mouse_move_delay)
                elif isinstance(data, mouse.ButtonEvent):
                    if data.event_type == mouse.UP:
                        mouse.press(data.button)
                        mouse.release(data.button)
                        time.sleep(mouse_click_delay)

                elif isinstance(data, mouse.WheelEvent):
                    mouse.wheel(data.delta)
                    time.sleep(mouse_scroll_delay)


def main():
    with open("recording_1.zvt", "rb") as f:
        data = pickle.load(f)
        playback = KeyboardAndMouseModulePlayback(data)
        playback.play(3.0)


if __name__ == "__main__":
    main()
