#!/usr/bin/env python3
import dataclasses, json, sys
from enum import Enum
from pathlib import Path
from typing import List
class TestStatus(Enum):
    PASSED = 1
    FAILED = 2
    SKIPPED = 3
    ERROR = 4
@dataclasses.dataclass
class TestResult:
    name: str
    status: TestStatus
### DO NOT MODIFY THE CODE ABOVE ###
### Implement the parsing logic below ###

import re
 
def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Parse pytest -v output and return one TestResult per test.
 
    Pytest verbose output lines have the form:
        tests/path/to/test.py::Class::test_name STATUS [ N%]
    where STATUS is PASSED, FAILED, SKIPPED, or ERROR.
 
    Both stdout and stderr are scanned so nothing is missed regardless of
    how the test runner routes its output.
    """
    results = []
    seen = set()
 
    status_map = {
        "PASSED":  TestStatus.PASSED,
        "FAILED":  TestStatus.FAILED,
        "SKIPPED": TestStatus.SKIPPED,
        "ERROR":   TestStatus.ERROR,
    }
 
    pattern = re.compile(
        r"^(tests/\S+)\s+(PASSED|FAILED|ERROR|SKIPPED)",
        re.MULTILINE,
    )
 
    combined = stdout_content + "\n" + stderr_content
 
    for match in pattern.finditer(combined):
        name = match.group(1)
        status_str = match.group(2)
        if name not in seen:
            seen.add(name)
            results.append(TestResult(name=name, status=status_map[status_str]))
 
    return results
 
### Implement the parsing logic above ###
### DO NOT MODIFY THE CODE BELOW ###
def export_to_json(results: List[TestResult], output_path: Path) -> None:
    json_results = {'tests': [{'name': r.name, 'status': r.status.name} for r in results]}
    with open(output_path, 'w') as f:
        json.dump(json_results, f, indent=2)
def main(stdout_path: Path, stderr_path: Path, output_path: Path) -> None:
    with open(stdout_path) as f: stdout_content = f.read()
    with open(stderr_path) as f: stderr_content = f.read()
    results = parse_test_output(stdout_content, stderr_content)
    export_to_json(results, output_path)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))