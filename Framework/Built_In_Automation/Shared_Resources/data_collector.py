# Author: Mohammed Sazid Al Rashid <sazidozon@gmail.com>


class DataCollector:
    def __init__(self):
        self.list_classes = [list, tuple]
        self.dict_classes = [dict]

    def set_list_classes(self, class_list):
        self.list_classes = class_list

    def set_dict_classes(self, class_list):
        self.dict_classes = class_list

    def _collect(self, collector, pattern, pos, data):
        if pos >= len(pattern):
            collector.append(data)
            return

        _type = type(data)
        _pattern = pattern[pos]

        if _type in self.list_classes:
            try:
                index = int(_pattern)
                self._collect(collector, pattern, pos + 1, data[index])
            except:
                if _pattern == "_":
                    for item in data:
                        self._collect(collector, pattern, pos + 1, item)
                return
        elif _type in self.dict_classes:
            if _pattern == "*":
                for key in data:
                    self._collect(collector, pattern, pos + 1, data[key])
            elif _pattern[-1] == "*":
                # If partial match from start = matchstart*
                partial_pattern = _pattern[:-1]
                for key in data:
                    if key.startswith(partial_pattern):
                        self._collect(collector, pattern, pos + 1, data[key])
            elif _pattern[0] == "*":
                # If partial match from end = *matchend
                partial_pattern = _pattern[1:]
                for key in data:
                    if key.endswith(partial_pattern):
                        self._collect(collector, pattern, pos + 1, data[key])
            else:
                try:
                    self._collect(collector, pattern, pos + 1, data[_pattern])
                except:
                    return

    def collect(self, pattern, data):
        """Extracts and collects data from the given initial data
        according to the pattern provided. The pattern can be either a comma
        separated string or a list or tuple.
        """
        if isinstance(pattern, str):
            pattern = [x.strip() for x in pattern.split(",")]

        collector = []
        self._collect(collector, pattern, 0, data)

        return collector


def main():
    # This function is for testing.
    
    ref_data = [
        {
            "error1": {
                "type": "Runtime Error",
                "occurrence": [
                    {"line": 10, "message": "fail"},
                    {"line": 20, "message": "block"},
                ],
            },
            "error2": {
                "type": "Compiler Error",
                "occurrence": (
                    {"line": 50, "message": "fail"},
                    {"line": 64, "message": "xyz"},
                    {"line": 70, "message": "pqr"},
                ),
            },
            "1error": {
                "type": "Runtime Error",
                "occurrence": [
                    {"line": 100, "message": "fail"},
                    {"line": 200, "message": "block"},
                ],
            },
            "2error": {
                "type": "Compiler Error",
                "occurrence": (
                    {"line": 500, "message": "fail"},
                    {"line": 640, "message": "xyz"},
                    {"line": 700, "message": "pqr"},
                ),
            },
        }
    ]

    collector = []

    patterns = (
        "_, *, occurrence, _, line",
        "_, error*, occurrence, _, line",
        "_, *error, occurrence, _, line",
        "_, *, occurrence, _, message",
        "_, error1, type",
        "0, error2, occurrence, 0, message",
    )

    assertions = (
        [10, 20, 50, 64, 70, 100, 200, 500, 640, 700],
        [10, 20, 50, 64, 70],
        [100, 200, 500, 640, 700],
        ['fail', 'block', 'fail', 'xyz', 'pqr', 'fail', 'block', 'fail', 'xyz', 'pqr'],
        ['Runtime Error'],
        ['fail'],
    )

    for pattern, assertion_data in zip(patterns, assertions):
        data_collector = DataCollector()
        collected = data_collector.collect(pattern, ref_data)

        assert(collected == assertion_data)
        print(collected)


if __name__ == "__main__":
    main()
