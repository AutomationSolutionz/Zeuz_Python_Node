import json
import traceback
from pathlib import Path
from pprint import pformat
from yapf.yapflib.yapf_api import FormatCode


def parse_common_information(data):
    """Parses common information that will be available to all test cases"""

    # For now, we only deal with one Run ID.
    run_id = list(data.keys())[0]
    data = data[run_id]

    test_cases = data["TestCases"]

    common = {**data}
    del common["TestCases"]

    return run_id, common, test_cases


def spaced_str(s, spaces_before=0):
    result = ""
    for line in s.split("\n"):
        if line:
            result += (" " * spaces_before) + line + "\n"
        else:
            result += line + "\n"

    return result


def pretty(data):
    printed_variables = []

    if isinstance(data, dict):
        for key in data:
            formatted_val = pformat(data[key], sort_dicts=True)
            key = key.replace(" ", "_")
            printed_variables.append(f"{key} = {formatted_val}\n")
    else:
        printed_variables.append(pformat(data, sort_dicts=True))

    return "".join(printed_variables)


def pp(data, spaces_before=0):
    print(spaced_str(pretty(data), spaces_before=spaces_before))


def parse_json(path):
    """Parses the json file at `path` into a python object"""

    try:
        with open(path, "r") as f:
            return json.loads(f.read())
    except:
        traceback.print_exc()
        return None


def write_test_case_data_to_files(run_id, common, test_cases, output_dir):
    output_dir = Path(output_dir)

    for test_case in test_cases:
        steps = test_case["Steps"]
        del test_case["Steps"]

        code = f"run_id = '{run_id}'\n"
        code += pretty(common)
        code += pretty(test_case) + "\n"

        for step in steps:
            actions = step["Step actions"]
            del step["Step actions"]

            step_name = ''.join(e for e in step["Step name"] if e.isalnum() or e == '_')

            code += f"""
def test_{step_name}():
{spaced_str(pretty(step), 4)}
    Step_actions = {spaced_str(pretty(actions), 4)}
"""

        code = FormatCode(code, style_config={
            "based_on_style": "pep8",
            "indent_width": 4,
            "split_before_logical_operator": False,
            "column_limit": 100,
            "ALLOW_SPLIT_BEFORE_DICT_VALUE": False,
            "COALESCE_BRACKETS": True,
            "FORCE_MULTILINE_DICT": True,
        })[0]

        # Save code to file
        filename = f"test_case_{test_case['TestCase no']}.py"
        print(output_dir / filename)
        with open(output_dir / filename, "w") as f:
            f.write(code)


def main(path=None, output_dir=None):
    if path is None:
        path = "test_cases_data.json"

    if output_dir is None:
        output_dir = Path.cwd() / "tests"
        # Create output folder if it does not exist (with parents)

    output_dir.mkdir(parents=True, exist_ok=True)

    data = parse_json(Path(path))

    if data is None:
        print("Failed to parse test case data. Make sure it is in 'json' format")
        return

    run_id, common, test_cases = parse_common_information(data)

    write_test_case_data_to_files(run_id, common, test_cases, output_dir)


if __name__ == "__main__":
    main("test_cases_data.json", Path.cwd() / "tests")
