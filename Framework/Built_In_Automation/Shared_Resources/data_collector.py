# Author: Mohammed Sazid Al Rashid <sazidozon@gmail.com>

import re


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
            filter_pattern = r"\|(.*?)\|"
            filters = re.findall(filter_pattern, _pattern)

            if len(filters) > 0:
                split_filters = [x.split(":") for x in filters]
                filters = dict()
                for k, v in split_filters:
                    if k in filters:
                        filters[k].append(v)
                    else:
                        filters[k] = [v,]

                # Boolean list of whether a particular filter matched or not
                matched_list = []
                for k in filters:
                    for v in filters[k]:
                        matched_list.append(k in data and data[k] == v)

                # Decide whether we should accept this match list.
                should_allow = False
                if len(filters) == 1:
                    should_allow = any(matched_list)
                elif len(filters) > 1 and all(matched_list):
                    should_allow = True

                if should_allow:
                    val = data[_pattern[:_pattern.find("|")]]
                    self._collect_pattern(collector, pattern, pos + 1, val)
            elif _pattern == "_all_":
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
    ref_data = {
        "data": {
            "filteredDevices": {
            "deviceSummaries": [
                {
                "id": 5,
                "cryptoPrimitives": []
                },
                {
                "id": 96,
                "cryptoPrimitives": []
                }
            ],
            "filterCategories": [
                {
                "categoryName": "Crypto",
                "filterGroups": [
                    {
                    "groupName": "Strength",
                    "searchTerm": "abc",
                    "filters": [
                        {
                        "name": "BROKEN",
                        "value": 10
                        },
                        {
                        "name": "MISUSED",
                        "value": 0
                        },
                        {
                        "name": "STANDARDIZED_QSC",
                        "value": 0
                        }
                    ]
                    },
                    {
                    "groupName": "Protocol",
                    "searchTerm": "xyz",
                    "filters": [
                        {
                        "name": "TLS 1.2",
                        "value": 3
                        },
                        {
                        "name": "TLS 1.3",
                        "value": 4
                        }
                    ]
                    }
                ]
                }
            ]
            }
        }
        }

    collector = []

    collector_patterns = (
        '''data,filteredDevices,filterCategories,_all_,filterGroups,_all_,filters|groupName:Protocol||searchTerm:xyz|,_all_,name''',
    )

    key_patterns = (
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
