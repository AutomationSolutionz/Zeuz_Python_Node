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

    ref_data = {
        "error": {
            "errors": [
                {
                    "message": 'Field "dataSourceScanSchedules" of type "[DataSourceScanSchedule!]!" must have a selection of subfields. Did you mean "dataSourceScanSchedules { ... }"?',
                    "locations": [{"line": 2, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Field "dataSourceScanSchedules" of type "[DataSourceScanSchedule!]!" must have a selection of subfields. Did you mean "dataSourceScanSchedules { ... }"?',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/ScalarLeafsRule.js:40:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Field "dataSourceScanSchedules" argument "where" of type "DataSourceScanScheduleWhere!" is required, but it was not provided.',
                    "locations": [{"line": 2, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Field "dataSourceScanSchedules" argument "where" of type "DataSourceScanScheduleWhere!" is required, but it was not provided.',
                                "    at Object.leave (/home/guardian/node_modules/graphql/validation/rules/ProvidedRequiredArgumentsRule.js:62:33)",
                                "    at Object.leave (/home/guardian/node_modules/graphql/language/visitor.js:344:29)",
                                "    at Object.leave (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:390:21)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "dataSource" on type "Query". Did you mean "dataSources" or "dataSourceCount"?',
                    "locations": [{"line": 3, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "dataSource" on type "Query". Did you mean "dataSources" or "dataSourceCount"?',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "lastStatus" on type "Query".',
                    "locations": [{"line": 6, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "lastStatus" on type "Query".',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "schedule" on type "Query".',
                    "locations": [{"line": 7, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "schedule" on type "Query".',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "name" on type "Query".',
                    "locations": [{"line": 8, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "name" on type "Query".',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "tag" on type "Query".',
                    "locations": [{"line": 9, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "tag" on type "Query".',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "scheduleActive" on type "Query".',
                    "locations": [{"line": 10, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "scheduleActive" on type "Query".',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "timezone" on type "Query".',
                    "locations": [{"line": 11, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "timezone" on type "Query".',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "cronish" on type "Query".',
                    "locations": [{"line": 12, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "cronish" on type "Query".',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "status" on type "Query".',
                    "locations": [{"line": 13, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "status" on type "Query".',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "addedBy" on type "Query".',
                    "locations": [{"line": 14, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "addedBy" on type "Query".',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
                {
                    "message": 'Cannot query field "addedAt" on type "Query".',
                    "locations": [{"line": 18, "column": 3}],
                    "extensions": {
                        "code": "GRAPHQL_VALIDATION_FAILED",
                        "exception": {
                            "stacktrace": [
                                'GraphQLError: Cannot query field "addedAt" on type "Query".',
                                "    at Object.Field (/home/guardian/node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:46:31)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/language/visitor.js:323:29)",
                                "    at Object.enter (/home/guardian/node_modules/graphql/utilities/TypeInfo.js:370:25)",
                                "    at visit (/home/guardian/node_modules/graphql/language/visitor.js:243:26)",
                                "    at Object.validate (/home/guardian/node_modules/graphql/validation/validate.js:69:24)",
                                "    at validate (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:221:34)",
                                "    at Object.<anonymous> (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:118:42)",
                                "    at Generator.next (<anonymous>)",
                                "    at fulfilled (/home/guardian/node_modules/apollo-server-core/dist/requestPipeline.js:5:58)",
                                "    at processTicksAndRejections (internal/process/task_queues.js:97:5)",
                            ]
                        },
                    },
                },
            ]
        }
    }

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
