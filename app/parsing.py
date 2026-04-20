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

import re

def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Parse pytest -v output and return one TestResult per discovered test case.

    Pytest verbose line format:
        tests/path.py::test_name PASSED   [ xx%]
        tests/path.py::test_name FAILED   [ xx%]
        tests/path.py::test_name SKIPPED (reason)  [ xx%]
        tests/path.py::test_name ERROR    [ xx%]

    Falls back to a single ERROR result when pytest fails before reporting
    any individual test (collection error, import error, etc.).
    """
    status_map = {
        "PASSED": TestStatus.PASSED,
        "FAILED": TestStatus.FAILED,
        "SKIPPED": TestStatus.SKIPPED,
        "ERROR": TestStatus.ERROR,
    }

    # Match: any::path::test_name STATUS [optional percentage]
    line_re = re.compile(
        r"^(\S+::(\S+?))\s+(PASSED|FAILED|SKIPPED|ERROR)\b",
        re.MULTILINE,
    )

    results: List[TestResult] = []
    seen: set = set()

    for m in line_re.finditer(stdout_content):
        full_name = m.group(1)
        if full_name in seen:
            continue
        seen.add(full_name)
        # Use the test node id (file::test_name) as the result name
        results.append(TestResult(name=full_name, status=status_map[m.group(3)]))

    if not results:
        # No per-test lines found — pytest failed before/during collection.
        # Capture the first meaningful error line from stderr or stdout.
        combined = (stderr_content + "\n" + stdout_content).strip()
        error_line = next(
            (ln.strip() for ln in combined.splitlines() if ln.strip()),
            "session error",
        )
        results.append(TestResult(name=error_line[:120], status=TestStatus.ERROR))

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
