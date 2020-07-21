# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import inspect
import copy
from Framework.Utilities import CommonUtil


MODULE_NAME = inspect.getmodulename(__file__)


def make_single_data_set_compatible(expected_list):
    _expected_tuple = [x for x in expected_list if len(x) == 4]
    _expected_group = [x for x in expected_list if len(x) > 4]
    _expected_tuple = [(x[0], "", x[1], x[2], x[3]) for x in _expected_tuple]
    e = list(_expected_tuple + _expected_group)
    return e


class CompareModule:
    def compare(self, expected_list, actual_list, keywordlist=[], ignorelist=[]):
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        expected_copy = copy.deepcopy(expected_list)
        actual_copy = copy.deepcopy(actual_list)

        if len(keywordlist) == 0:
            return single_dataset_compare(expected_copy[0], actual_copy[0])
        else:
            data_return_expected = eliminate_duplicate(expected_copy, keywordlist)
            expected_copy = copy.deepcopy(data_return_expected["valid"])
            duplicate_expected = copy.deepcopy(data_return_expected["duplicate"])

            data_return_actual = eliminate_duplicate(actual_copy, keywordlist)
            actual_copy = copy.deepcopy(data_return_actual["valid"])
            duplicate_actual = copy.deepcopy(data_return_actual["duplicate"])

            dataset_without_keyfield_expected = []
            dataset_with_keyfield_expected = []
            # strip out all the entry that do not have the keyword as specified
            for index in range(len(expected_copy) - 1, -1, -1):
                each = expected_copy[index]
                temp_keyfield = find_keylist(each)
                if len(temp_keyfield) == 0:
                    dataset_without_keyfield_expected.append(each)
                    expected_copy.pop(index)
                else:
                    matching_keyfield = list(set(temp_keyfield) & set(keywordlist))
                    extra_keyfield_in_expected = list(
                        set(temp_keyfield) - set(keywordlist)
                    )
                    missing_keyfield_in_expected = list(
                        set(keywordlist) - set(temp_keyfield)
                    )
                    if (
                        len(extra_keyfield_in_expected) == 0
                        and len(missing_keyfield_in_expected) == 0
                    ):
                        dataset_with_keyfield_expected.append(each)
                        expected_copy.pop(index)
                    else:
                        dataset_without_keyfield_expected.append(each)
                        expected_copy.pop(index)
            dataset_without_keyfield_actual = []
            dataset_with_keyfield_actual = []
            for index in range(len(actual_copy) - 1, -1, -1):
                each = actual_copy[index]
                temp_keyfield = find_keylist(each)
                if len(temp_keyfield) == 0:
                    dataset_without_keyfield_actual.append(each)
                    actual_copy.pop(index)
                else:
                    matching_keyfield = list(set(temp_keyfield) & set(keywordlist))
                    extra_keyfield_in_expected = list(
                        set(temp_keyfield) - set(keywordlist)
                    )
                    missing_keyfield_in_expected = list(
                        set(keywordlist) - set(temp_keyfield)
                    )
                    if (
                        len(extra_keyfield_in_expected) == 0
                        and len(missing_keyfield_in_expected) == 0
                    ):
                        dataset_with_keyfield_actual.append(each)
                        actual_copy.pop(index)
                    else:
                        dataset_without_keyfield_actual.append(each)
                        actual_copy.pop(index)
            for_extra_expected = copy.deepcopy(dataset_with_keyfield_expected)
            for_extra_actual = copy.deepcopy(dataset_with_keyfield_actual)

            matching_list = []
            for iExp in range(len(dataset_with_keyfield_expected) - 1, -1, -1):
                current_expected = dataset_with_keyfield_expected[iExp]
                for iAct in range(len(dataset_with_keyfield_actual) - 1, -1, -1):
                    current_actual = dataset_with_keyfield_actual[iAct]
                    match_tag = match_dataset(
                        current_expected, current_actual, keywordlist
                    )
                    if match_tag:
                        temp = []
                        temp.append(current_expected)
                        temp.append(current_actual)
                        dataset_with_keyfield_expected.pop(iExp)
                        dataset_with_keyfield_actual.pop(iAct)
                        matching_list.append(tuple(temp))
            missing_datasets = copy.deepcopy(dataset_with_keyfield_expected)
            for iAct in range(len(for_extra_actual) - 1, -1, -1):
                current_actual = for_extra_actual[iAct]
                for iExp in range(len(for_extra_expected) - 1, -1, -1):
                    current_expected = for_extra_expected[iExp]
                    match_tag = match_dataset(
                        current_expected, current_actual, keywordlist
                    )
                    if match_tag:
                        for_extra_actual.pop(iAct)
                        for_extra_expected.pop(iExp)
            extra_datasets = copy.deepcopy(for_extra_actual)
            if (
                len(dataset_without_keyfield_actual) > 0
                or len(dataset_without_keyfield_expected) > 0
                or len(missing_datasets) > 0
                or len(extra_datasets) > 0
            ):
                status_flag = 3
            else:
                status_flag = 1
            status = []
            tag = "Matching"
            CommonUtil.ExecLog(
                sModuleInfo, "%s Datasets: %d" % (tag, len(matching_list)), status_flag
            )
            for i, each in enumerate(matching_list):
                CommonUtil.ExecLog(
                    sModuleInfo, "%s Dataset: #%d" % (tag, (i + 1)), status_flag
                )
                expected_list = each[0]
                actual_list = each[1]
                status.append(single_dataset_compare(expected_list, actual_list))
            # convert datasets to for printing
            non_key_field_expected = convert_to_print_format(
                dataset_without_keyfield_expected
            )
            non_key_field_actual = convert_to_print_format(
                dataset_without_keyfield_actual
            )

            missing_datasets = convert_to_print_format(missing_datasets)
            extra_datasets = convert_to_print_format(extra_datasets)
            expected_duplicate = convert_to_print_format(duplicate_expected)
            actual_duplicate = convert_to_print_format(duplicate_actual)
            log_to_db(sModuleInfo, missing_datasets, "Missing", status_flag)
            log_to_db(sModuleInfo, extra_datasets, "Extra", status_flag)
            log_to_db(
                sModuleInfo, non_key_field_expected, "KeyField Missing", status_flag
            )
            log_to_db(sModuleInfo, non_key_field_actual, "KeyField Extra", status_flag)
            log_to_db(
                sModuleInfo, expected_duplicate, "Duplicate in Expected", status_flag
            )
            log_to_db(sModuleInfo, actual_duplicate, "Duplicate in Actual", status_flag)
            if (
                len(dataset_without_keyfield_actual) > 0
                or len(dataset_without_keyfield_expected) > 0
                or len(missing_datasets) > 0
                or len(extra_datasets) > 0
            ):
                return "Failed"
            else:
                tag = True
                for each in status:
                    if each != "Passed":
                        tag = False
                    if not tag:
                        break
                if tag:
                    return "Passed"
                else:
                    return "Failed"


def log_to_db(sModuleInfo, datasets, tag, status):
    CommonUtil.ExecLog(sModuleInfo, "%s Datasets: %d" % (tag, len(datasets)), status)
    for i, eachdataset in enumerate(datasets):
        CommonUtil.ExecLog(sModuleInfo, "%s Dataset: #%d" % (tag, (i + 1)), status)
        tuple_data = []
        for eachitem in eachdataset:
            if isinstance(eachitem[1], str):
                tuple_data.append(eachitem)
        CommonUtil.ExecLog(
            sModuleInfo,
            "%s Tuple Data Entry Count: %d" % (tag, len(tuple_data)),
            status,
        )
        for j, eachitem in enumerate(tuple_data):
            CommonUtil.ExecLog(
                sModuleInfo,
                "#%d : %s : %s" % ((j + 1), eachitem[0], eachitem[1]),
                status,
            )
        for j, eachitem in enumerate(eachdataset):
            if isinstance(eachitem[1], list):
                CommonUtil.ExecLog(
                    sModuleInfo, "%s Group Data Label: %s" % (tag, eachitem[0]), status
                )
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "%s Group Data Entry Count: %d" % (tag, len(eachitem[1])),
                    status,
                )
                for k, eachdata in enumerate(eachitem[1]):
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "#%d : %s : %s" % ((k + 1), eachdata[0], eachdata[1]),
                        status,
                    )


def convert_to_print_format(dataset):
    final_dataset_convert = []
    for each in dataset:
        temp = []
        group_data_label = []
        for i, eachitem in enumerate(each):
            if eachitem[1] != "":
                if eachitem[0] not in group_data_label:
                    group_data_label.append(eachitem[0])
            else:
                temp.append((eachitem[0], eachitem[2]))
        for eachitem in group_data_label:
            temp_label = eachitem
            temp_array = []
            for tempitem in each:
                if tempitem[0] == temp_label:
                    temp_array.append((tempitem[1], tempitem[2]))
            temp.append((temp_label, temp_array))
        final_dataset_convert.append(temp)
    return final_dataset_convert


def match_dataset(expected, actual, keywordlist):
    tag = True
    for each in keywordlist:
        expected_value = ""
        actual_value = ""
        for eachitem in expected:
            if each == eachitem[0] and eachitem[1] == "" and eachitem[3]:
                expected_value = eachitem[2]
                break
        for eachitem in actual:
            if each == eachitem[0] and eachitem[1] == "" and eachitem[3]:
                actual_value = eachitem[2]
                break
        if expected_value != actual_value or actual_value == "" or expected_value == "":
            tag = False
        if not tag:
            break
    return tag


def eliminate_duplicate(datasets, keywordlist):
    given_datasets = copy.deepcopy(datasets)
    temp = []
    for index in range(len(given_datasets) - 1, -1, -1):
        temp.append(given_datasets[index])
    given_datasets = copy.deepcopy(temp)
    data_to_consider = []
    data_to_eliminate = []
    index = len(given_datasets) - 1
    while index >= 0:
        current_data = given_datasets[index]
        data_to_consider.append(current_data)
        given_datasets.pop(index)
        for i in range(len(given_datasets) - 1, -1, -1):
            data = given_datasets[i]
            match_tag = match_dataset(current_data, data, keywordlist)
            if match_tag:
                data_to_eliminate.append(data)
                given_datasets.pop(i)
        index = len(given_datasets) - 1
    result = {"valid": data_to_consider, "duplicate": data_to_eliminate}
    return result


def single_dataset_compare(expected_copy, actual_copy):
    expected_copy = make_single_data_set_compatible(expected_copy)
    actual_copy = make_single_data_set_compatible(actual_copy)
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    expected_list = copy.deepcopy(expected_copy)
    actual_list = copy.deepcopy(actual_copy)
    # take out the group data here
    expected_group_data = []
    expected_tuple_data = []
    for index in range(len(expected_list) - 1, -1, -1):
        element = expected_list[index]
        # ignore_list compare here
        if element[4]:
            expected_list.pop(index)
        else:
            if element[1] == "":
                expected_tuple_data.append((element[0], element[1], element[2]))
            else:
                expected_group_data.append((element[0], element[1], element[2]))
    actual_tuple_data = []
    actual_group_data = []
    for index in range(len(actual_list) - 1, -1, -1):
        element = actual_list[index]
        # ignore_list compare here
        if element[4]:
            actual_list.pop(index)
        else:
            if element[1] == "":
                actual_tuple_data.append((element[0], element[1], element[2]))
            else:
                actual_group_data.append((element[0], element[1], element[2]))
    matching_tuple_data = list(set(expected_tuple_data) & set(actual_tuple_data))
    missing_tuple_data = list(set(expected_tuple_data) - set(actual_tuple_data))
    extra_tuple_data = list(set(actual_tuple_data) - set(expected_tuple_data))

    matching_group_data = list(set(expected_group_data) & set(actual_group_data))
    missing_group_data = list(set(expected_group_data) - set(actual_group_data))
    extra_group_data = list(set(actual_group_data) - set(expected_group_data))

    matching_group_record_label = list(set([x[0] for x in matching_group_data]))
    final = []
    for each in matching_group_record_label:
        temp_label = each
        temp = []
        for eachitem in matching_group_data:
            if temp_label == eachitem[0]:
                temp.append((eachitem[1], eachitem[2]))
        final.append((temp_label, temp))
    matching_group_data = final

    missing_group_data_label = list(set([x[0] for x in missing_group_data]))

    final_missing_group_data = []
    for each in missing_group_data_label:
        temp_label = each
        temp = []
        for eachitem in missing_group_data:
            if temp_label == eachitem[0]:
                temp.append((eachitem[1], eachitem[2]))
        final_missing_group_data.append((temp_label, temp))

    extra_group_data_label = list(set([x[0] for x in extra_group_data]))

    final_extra_group_data = []
    for each in extra_group_data_label:
        temp_label = each
        temp = []
        for eachitem in extra_group_data:
            if temp_label == eachitem[0]:
                temp.append((eachitem[1], eachitem[2]))
        final_extra_group_data.append((temp_label, temp))

    # match the group data missing compare
    group_data_not_matching = []
    for index in range(len(final_missing_group_data) - 1, -1, -1):
        element = final_missing_group_data[index]
        for actindex in range(len(final_extra_group_data) - 1, -1, -1):
            data_to_compare = final_extra_group_data[actindex]
            if element[0] == data_to_compare[0]:
                label = element[0]
                temp_expected = []
                temp_actual = []

                _key_list = [x[0] for x in element[1]]

                for e in _key_list:
                    _e = [x for x in element[1] if x[0] == e]
                    _a = [x for x in data_to_compare[1] if x[0] == e]
                    if _e and _a:
                        temp_expected.append(_e[0])
                        temp_actual.append(_a[0])

                expected_tuple = [label, temp_expected]
                actual_tuple = [label, temp_actual]
                group_data_not_matching.append(
                    (tuple(expected_tuple), tuple(actual_tuple))
                )

                # for i in range(len(element[1])-1,-1,-1):
                #     for j in range(len(data_to_compare[1])-1,-1,-1):
                #         if element[1][i][0]==data_to_compare[1][j][0]:
                #             temp_expected.append(element[1][i])
                #             temp_actual.append(data_to_compare[1][j])
                #             element[1].pop(i)
                #             data_to_compare[1].pop(j)
                # expected_tuple=[label,temp_expected]
                # actual_tuple=[label,temp_actual]
                # group_data_not_matching.append((tuple(expected_tuple),tuple(actual_tuple)))
    _final_missing = []
    _final_extra = []
    for e in group_data_not_matching:
        # missing data remove
        _e = [x for x in final_missing_group_data if x[0] == e[0][0]]
        _a = [x for x in final_extra_group_data if x[0] == e[0][0]]

        if _e:
            for i in e[0][1]:
                for each in final_missing_group_data:
                    f = [x for x in each[1] if x[0] == i[0]]
                    if f:
                        each[1].remove(f[0])
        if _a:
            for i in e[1][1]:
                for each in final_extra_group_data:
                    f = [x for x in each[1] if x[0] == i[0]]
                    if f:
                        each[1].remove(f[0])

    final_missing_group_data = [x for x in final_missing_group_data if len(x[1]) > 0]
    final_extra_group_data = [x for x in final_extra_group_data if len(x[1]) > 0]
    if (
        len(missing_tuple_data) > 0
        or len(extra_tuple_data) > 0
        or len(final_missing_group_data) > 0
        or len(final_extra_group_data)
        or len(group_data_not_matching) > 0
    ):
        status = 3
    else:
        status = 1
    CommonUtil.ExecLog(
        sModuleInfo, "Matching Records: %d" % len(matching_tuple_data), status
    )
    for i, each in enumerate(matching_tuple_data):
        CommonUtil.ExecLog(
            sModuleInfo,
            "#%d : %s : %s : %s" % ((i + 1), each[0], each[2], each[2]),
            status,
        )

    CommonUtil.ExecLog(
        sModuleInfo, "Missing Records: %d" % len(missing_tuple_data), status
    )
    for i, each in enumerate(missing_tuple_data):
        element = each
        found = False
        for j, eachitem in enumerate(extra_tuple_data):
            if (element[0], element[1]) == (eachitem[0], eachitem[1]):
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "#%d : %s : %s : %s"
                    % ((j + 1), element[0], element[2], eachitem[2]),
                    status,
                )
                extra_tuple_data.pop(j)
                found = True
                break
        if not found:
            CommonUtil.ExecLog(
                sModuleInfo,
                "#%d : %s : %s : %s" % ((i + 1), element[0], element[2], "N/A"),
                status,
            )
    CommonUtil.ExecLog(sModuleInfo, "Extra Records: %d" % len(extra_tuple_data), status)
    for i, each in enumerate(extra_tuple_data):
        CommonUtil.ExecLog(
            sModuleInfo,
            "#%d : %s : %s : %s" % ((i + 1), each[0], "N/A", each[2]),
            status,
        )

    CommonUtil.ExecLog(
        sModuleInfo, "Matching Group Records: %d" % len(matching_group_data), status
    )
    for i, each in enumerate(matching_group_data):
        CommonUtil.ExecLog(sModuleInfo, "Matching Group Record: #%d" % (i + 1), status)
        CommonUtil.ExecLog(sModuleInfo, "Matching Group Label: %s" % each[0], status)
        CommonUtil.ExecLog(
            sModuleInfo, "Matching Group Entry Count: %d" % len(each[1]), status
        )
        for j, eachitem in enumerate(each[1]):
            CommonUtil.ExecLog(
                sModuleInfo,
                "#%d : %s : %s : %s" % ((j + 1), eachitem[0], eachitem[1], eachitem[1]),
                status,
            )
    final_list = []
    for each in group_data_not_matching:
        temp_label = each[0][0]
        expected_data = each[0][1]
        actual_data = each[1][1]
        temp = []
        for eachitem in expected_data:
            for eachitemtemp in actual_data:
                if eachitem[0] == eachitemtemp[0]:
                    temp.append((eachitem[0], eachitem[1], eachitemtemp[1]))
        final_list.append((temp_label, temp))
    CommonUtil.ExecLog(
        sModuleInfo, "Non Match Group Data: %d" % len(final_list), status
    )
    for each in final_list:
        CommonUtil.ExecLog(sModuleInfo, "Non Match Group Label: %s" % each[0], status)
        CommonUtil.ExecLog(
            sModuleInfo, "Non Match Group Entry Count: %d" % len(each[1]), status
        )
        for i, eachitem in enumerate(each[1]):
            CommonUtil.ExecLog(
                sModuleInfo,
                "#%d : %s : %s :%s" % ((i + 1), eachitem[0], eachitem[1], eachitem[2]),
                status,
            )
    CommonUtil.ExecLog(
        sModuleInfo, "Missing Group Data: %d" % len(final_missing_group_data), status
    )
    for each in final_missing_group_data:
        CommonUtil.ExecLog(sModuleInfo, "Missing Group Label: %s" % each[0], status)
        CommonUtil.ExecLog(
            sModuleInfo, "Missing Group Entry Count: %d" % len(each[1]), status
        )
        for i, eachitem in enumerate(each[1]):
            CommonUtil.ExecLog(
                sModuleInfo,
                "#%d : %s : %s : %s" % ((i + 1), eachitem[0], eachitem[1], "N/A"),
                status,
            )
    CommonUtil.ExecLog(
        sModuleInfo, "Extra Group Data: %d" % len(final_extra_group_data), status
    )
    for each in final_extra_group_data:
        CommonUtil.ExecLog(sModuleInfo, "Extra Group Label: %s" % each[0], status)
        CommonUtil.ExecLog(
            sModuleInfo, "Extra Group Entry Count: %d" % len(each[1]), status
        )
        for i, eachitem in enumerate(each[1]):
            CommonUtil.ExecLog(
                sModuleInfo,
                "#%d : %s : %s : %s" % ((i + 1), eachitem[0], "N/A", eachitem[1]),
                status,
            )

    if status == 1:
        return "Passed"
    else:
        return "Failed"


def find_keylist(list_element):
    key_list = []
    for each in list_element:
        if each[1] == "":
            if each[3] and not each[4]:
                if each[0] not in key_list:
                    key_list.append(each[0])
    return key_list


def main():
    oCompare = CompareModule()

    # expected_list=[
    #                [
    #                 ('Address', 'hall', 'titumir', False, False),
    #                 ('Address', 'district', 'cox\'s bazar', False, False),
    #                 ('name', '', 'shetu', True, False),
    #                 ('roll', '', '0905011', True, False),
    #                 ('Academic', 'dept', 'me', False, False),
    #                 ('Academic', 'cg', '3.25', False, False)
    #                 ],
    #                [
    #                 ('name', '', 'shetu', True, False),
    #                 ('roll', '', '0905011', True, False),
    #                 ('Academic', 'dept', 'mme', False, False),
    #                 ],
    #                [
    #                 ('Address', 'hall', 'titumir', False, False),
    #                 ('Address', 'district', 'cox\'s bazar', False, False),
    #                 ('name', '', 'minar', True, False),
    #                 ('roll', '', '09050105', True, False),
    #                 ('Academic', 'dept', 'cse', False, False),
    #                 ('Academic', 'cg', '3.25', False, False)
    #                 ],
    #                [
    #                 ('name', '', 'shetu', True, False),
    #                 ('roll', '', '0905011', True, False),
    #                 ('Academic', 'dept', 'eee', False, False),
    #                 ],
    #                [
    #                 ('Address', 'hall', 'titumir', False, False),
    #                 ('Address', 'district', 'cox\'s bazar', False, False),
    #                 ('name', '', 'Saad', True, False),
    #                 ('roll', '', '09050105', False, False),
    #                 ('Academic', 'dept', 'cse', False, False),
    #                 ('Academic', 'cg', '3.25', False, False)
    #                 ]
    #                ]
    # actual_list=[
    #              [
    #                 ('Address', 'hall', 'titumir', False, False),
    #                 ('Address', 'district', 'cox\'s bazar', False, False),
    #                 ('name', '', 'shetu', True, False),
    #                 ('roll', '', '0905011', True, False),
    #                 ('Academic', 'dept', 'cse', False, False),
    #                 ('Academic', 'cg', '3.25', False, False)
    #                 ],
    #              [
    #                 ('Address', 'hall', 'titumir', False, False),
    #                 ('Address', 'district', 'cox\'s bazar', False, False),
    #                 ('name', '', 'hamid', False, False),
    #                 ('roll', '', '09050105', True, False),
    #                 ('Academic', 'dept', 'cse', False, False),
    #                 ('Academic', 'cg', '3.25', False, False)
    #                 ],
    #              [
    #                 ('Address', 'hall', 'titumir', False, False),
    #                 ('Address', 'district', 'cox\'s bazar', False, False),
    #                 ('name', '', 'Sajjad', True, False),
    #                 ('roll', '', '09050105', True, False),
    #                 ('Academic', 'dept', 'cse', False, False),
    #                 ('Academic', 'cg', '3.25', False, False)
    #                 ],
    #              [
    #                 ('name', '', 'Sajjad', True, False),
    #                 ('roll', '', '09050105', True, False),
    #             ]
    #             ]
    # keyword_list=['name','roll']
    expected_list = [
        [
            ("Starting from*", "car1", "101,770", False, False),
            ("Starting from*", "car2", "151,100", False, False),
            ("Starting from*", "car3", "118,900", False, False),
            ("Starting from*", "car4", "60,000", False, False),
            ("Destination Charge", "car1", "1,595", False, False),
            ("Destination Charge", "car2", "995", False, False),
            ("Destination Charge", "car3", "1,250", False, False),
            ("Destination Charge", "car4", "995", False, False),
        ]
    ]
    actual_list = [
        [
            ("Starting from*", "car1", "$101,770", False, False),
            ("Starting from*", "car2", "$20,995", False, False),
            ("Starting from*", "car3", "$20,995", False, False),
            ("Starting from*", "car4", "$20,995", False, False),
            ("Destination Charge", "car1", "$1,595", False, False),
            ("Destination Charge", "car2", "$810", False, False),
            ("Destination Charge", "car3", "$810", False, False),
            ("Destination Charge", "car4", "$810", False, False),
        ]
    ]
    status = oCompare.compare(expected_list, actual_list)
    print(status)


if __name__ == "__main__":
    main()
