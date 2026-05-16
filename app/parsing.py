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
    Parse pytest verbose output and extract test results.

    Expects lines like:
        tests/test_parse.py::TestClass::test_name PASSED
        tests/test_parse.py::test_name FAILED
    """
    results: List[TestResult] = []
    status_map = {
        "PASSED": TestStatus.PASSED,
        "FAILED": TestStatus.FAILED,
        "SKIPPED": TestStatus.SKIPPED,
        "ERROR": TestStatus.ERROR,
    }
    pattern = re.compile(r"^(\S+::\S+)\s+(PASSED|FAILED|SKIPPED|ERROR)")
    combined = stdout_content + "\n" + stderr_content
    for line in combined.splitlines():
        line = line.strip()
        match = pattern.match(line)
        if match:
            results.append(
                TestResult(name=match.group(1), status=status_map[match.group(2)])
            )
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