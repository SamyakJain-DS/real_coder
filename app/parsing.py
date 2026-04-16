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
    Parse pytest -v output and extract individual test results.
 
    Pytest -v produces lines of the form:
        tests/test_bike_workshop.py::ClassName::method_name PASSED [  1%]
        tests/test_bike_workshop.py::ClassName::method_name FAILED [  2%]
    """
    import re
 
    status_map = {
        "PASSED":  TestStatus.PASSED,
        "FAILED":  TestStatus.FAILED,
        "ERROR":   TestStatus.ERROR,
        "SKIPPED": TestStatus.SKIPPED,
    }
 
    # Match pytest -v lines: <nodeid> <STATUS> [percentage]
    pattern = re.compile(
        r"^(tests/[^\s]+\.py(?:::[^\s]+)+)\s+(PASSED|FAILED|ERROR|SKIPPED)",
        re.MULTILINE,
    )
 
    results: List[TestResult] = []
    seen: set = set()
 
    for content in (stdout_content, stderr_content):
        for match in pattern.finditer(content):
            name = match.group(1)
            status_str = match.group(2)
            if name not in seen:
                seen.add(name)
                results.append(TestResult(name=name, status=status_map[status_str]))
 
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