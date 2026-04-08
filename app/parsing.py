#!/usr/bin/env python3
import dataclasses
import json
import sys
from enum import Enum
from pathlib import Path
from typing import List

class TestStatus(Enum):
    """The test status enum."""
    PASSED = 1
    FAILED = 2
    SKIPPED = 3
    ERROR = 4

@dataclasses.dataclass
class TestResult:
    """The test result dataclass."""
    name: str
    status: TestStatus

### DO NOT MODIFY THE CODE ABOVE ###
### Implement the parsing logic below ###
 
def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Read JUnit XML reports written to /tmp/junit-reports/ by run.sh
    and return one TestResult per test case.
    """
    import glob
    import xml.etree.ElementTree as ET
 
    results = []
    seen = set()
 
    for report_file in sorted(glob.glob('/tmp/junit-reports/*.xml')):
        try:
            root = ET.parse(report_file).getroot()
            if root.tag == 'testsuites':
                testsuites = root.findall('testsuite')
            elif root.tag == 'testsuite':
                testsuites = [root]
            else:
                continue
 
            for testsuite in testsuites:
                for testcase in testsuite.findall('testcase'):
                    classname = testcase.get('classname', '')
                    name = testcase.get('name', '')
                    test_id = f"{classname}::{name}"
 
                    if test_id in seen:
                        continue
                    seen.add(test_id)
 
                    if testcase.find('failure') is not None or testcase.find('error') is not None:
                        status = TestStatus.FAILED
                    elif testcase.find('skipped') is not None:
                        status = TestStatus.SKIPPED
                    else:
                        status = TestStatus.PASSED
 
                    results.append(TestResult(name=test_id, status=status))
        except ET.ParseError:
            continue
 
    return results
 
### Implement the parsing logic above ###
### DO NOT MODIFY THE CODE BELOW ###

def export_to_json(results: List[TestResult], output_path: Path) -> None:
    json_results = {
        'tests': [
            {'name': result.name, 'status': result.status.name} for result in results
        ]
    }
    with open(output_path, 'w') as f:
        json.dump(json_results, f, indent=2)

def main(stdout_path: Path, stderr_path: Path, output_path: Path) -> None:
    with open(stdout_path) as f:
        stdout_content = f.read()
    with open(stderr_path) as f:
        stderr_content = f.read()

    results = parse_test_output(stdout_content, stderr_content)
    export_to_json(results, output_path)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python parsing.py <stdout_file> <stderr_file> <output_json>')
        sys.exit(1)

    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))