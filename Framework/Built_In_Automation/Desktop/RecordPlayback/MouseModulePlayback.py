import pickle
import mouse


class MouseModulePlayback:
    def __init__(self, data) -> None:
        self.data = data


    def play(self, speed_factor=1.0) -> None:
        if not self.data:
            raise RuntimeError("`data` cannot be None")
        if "events" not in self.data:
            raise RuntimeError("`data['events']` cannot be None")

        mouse.play(self.data["events"], speed_factor=speed_factor)
        mouse.unhook_all()


def main():
    with open("recording_1.zvt", "rb") as f:
        data = pickle.load(f)
        playback = MouseModulePlayback(data)
        playback.play(3.0)


if __name__ == "__main__":
    main()
