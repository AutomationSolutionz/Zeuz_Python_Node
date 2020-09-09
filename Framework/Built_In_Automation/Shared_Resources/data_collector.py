# Author: Mohammed Sazid Al Rashid <sazidozon@gmail.com>


class DataCollector:
    def __init__(self):
        self.list_classes = [list, tuple]
        self.dict_classes = [dict]

    def set_list_classes(self, class_list):
        self.list_classes = class_list

    def set_dict_classes(self, class_list):
        self.dict_classes = class_list

    def _collect_pattern(self, collector, pattern, pos, data):
        if pos >= len(pattern):
            collector.append(data)
            return

        _type = type(data)
        _pattern = pattern[pos]

        if _type in self.list_classes:
            try:
                index = int(_pattern)
                self._collect_pattern(collector, pattern, pos + 1, data[index])
            except:
                if _pattern == "_all_":
                    for item in data:
                        self._collect_pattern(collector, pattern, pos + 1, item)
                return
        elif _type in self.dict_classes:
            if _pattern == "_all_":
                for key in data:
                    self._collect_pattern(collector, pattern, pos + 1, data[key])
            elif _pattern[-1] == "*":
                # If partial match from start = matchstart*
                partial_pattern = _pattern[:-1]
                for key in data:
                    if key.startswith(partial_pattern):
                        self._collect_pattern(collector, pattern, pos + 1, data[key])
            elif _pattern[0] == "*":
                # If partial match from end = *matchend
                partial_pattern = _pattern[1:]
                for key in data:
                    if key.endswith(partial_pattern):
                        self._collect_pattern(collector, pattern, pos + 1, data[key])
            else:
                try:
                    self._collect_pattern(collector, pattern, pos + 1, data[_pattern])
                except:
                    return

    def _collect_key(self, collector, pattern, data):
        if not data:
            return

        _type = type(data)

        if _type in self.list_classes:
            for item in data:
                self._collect_key(collector, pattern, item)
        elif _type in self.dict_classes:
            for key in data:
                if key == pattern:
                    collector.append(data[key])
                    return
                self._collect_key(collector, pattern, data[key])

    def collect(self, pattern, data, collection_type):
        """Extracts and collects data from the given initial data
        according to the pattern provided. The pattern can be either a comma
        separated string or a list or tuple.
        """
        if isinstance(pattern, str):
            pattern = [x.strip() for x in pattern.split(",")]

        collector = None
        if collection_type == "pattern":
            collector = list()
            self._collect_pattern(collector, pattern, 0, data)
        elif collection_type == "key":
            collector = dict()
            for key in pattern:
                collector[key] = list()
                self._collect_key(collector[key], key, data)

        return collector


def main():
    # This function is for testing.

    # Put data here.
    ref_data = {}

    collector = []

    collector_patterns = ("error, errors, _, locations, _, line",)

    key_patterns = (
        "line, code, message",
    )

    data_collector = DataCollector()
    print("Pattern collector")
    for pattern in collector_patterns:
        print(data_collector.collect(pattern, ref_data, "pattern"))

    print("Key collector")
    for pattern in key_patterns:
        print(data_collector.collect(pattern, ref_data, "key"))


if __name__ == "__main__":
    main()
