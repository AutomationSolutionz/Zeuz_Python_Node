import xml.etree.ElementTree as ET
import json

# Spec:
# https://www.ibm.com/support/knowledgecenter/SSQ2R2_9.1.1/com.ibm.rsar.analysis.codereview.cobol.doc/topics/cac_useresults_junit.html


def process(data, save_path="report.xml"):
    # For now we'll only deal with one run-id
    data = data[0]

    testsuite = ET.Element("testsuite")
    testsuite.set("id", data["run_id"])

    if "objective" in data:
        testsuite.set("name", data["objective"])
    else:
        testsuite.set("name", data["TestObjective"])

    testsuite.set("tests", str(len(data["test_cases"])))
    testsuite.set("duration", data["execution_detail"]["duration"])
    testsuite.set("timestamp", data["execution_detail"]["teststarttime"])

    # Number of failed test cases.
    failures = 0

    for tc in data["test_cases"]:
        testcase = ET.SubElement(testsuite, "testcase")
        testcase.set("id", tc["testcase_no"])
        testcase.set("name", tc["title"])
        testcase.set("time", tc["execution_detail"]["duration"])

        if tc["execution_detail"]["status"].lower() == "passed":
            # Skip passed test cases.
            continue

        # Failure/error details related code.
        failures += 1
        try:
            for step in tc["steps"]:
                if step["execution_detail"]["status"].lower() == "passed":
                    # Skip passed steps.
                    continue
                failure = ET.SubElement(testcase, "failure")
                failure.set("type", step["step_name"])
                failure.set("message", step["step_name"] + " failed")
                failure.text = tc["execution_detail"]["failreason"]
        except:
            pass

    testsuite.set("failures", str(failures))

    ET.ElementTree(testsuite).write(
        save_path,
        encoding="UTF-8",
        xml_declaration=True
    )


def main():
    data = None
    with open("reporting/sample.json", "r") as f:
        data = json.loads(f.read())

    #print(data)
    process(data, "reporting/report.xml")


if __name__ == "__main__":
    main()
