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
    Parse pytest verbose output and extract individual test results.
 
    Matches lines of the form produced by pytest -v --tb=short --no-header:
        tests/test_foo.py::ClassName::test_method PASSED  [ 10%]
        tests/test_foo.py::ClassName::test_method FAILED  [ 20%]
        tests/test_foo.py::ClassName::test_method SKIPPED [ 30%]
        tests/test_foo.py::ClassName::test_method ERROR   [ 40%]
    """
    import re
    results = []
    seen = set()
 
    status_map = {
        "PASSED": TestStatus.PASSED,
        "FAILED": TestStatus.FAILED,
        "SKIPPED": TestStatus.SKIPPED,
        "ERROR": TestStatus.ERROR,
    }
 
    # Anchor to start of line; test node IDs contain no whitespace.
    # The status keyword follows one or more spaces, then optional trailing text.
    pattern = re.compile(
        r"^(tests/[^\s]+)\s+(PASSED|FAILED|SKIPPED|ERROR)",
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