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

STATUS_LINE = re.compile(r"^\s*(PASSED|FAILED|SKIPPED|ERROR)\s+(\S.*?)\s*$")

STATUS_TO_ENUM = {
    "PASSED": TestStatus.PASSED,
    "FAILED": TestStatus.FAILED,
    "SKIPPED": TestStatus.SKIPPED,
    "ERROR": TestStatus.ERROR,
}


def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Parse the runner's output and return one TestResult per status line found.

    The runner prints lines of the form '  PASSED <name>' or '  FAILED <name>'.
    SKIPPED/ERROR are recognised too so the parser stays faithful to the
    four-state TestStatus enum if the runner ever emits them. Tests that do
    not appear in the output are simply omitted; downstream validation is
    responsible for any normalisation across the four states.
    """
    seen = {}
    for line in (stdout_content + "\n" + stderr_content).splitlines():
        match = STATUS_LINE.match(line)
        if not match:
            continue
        status_word, name = match.group(1), match.group(2).strip()
        if name and name not in seen:
            seen[name] = STATUS_TO_ENUM[status_word]

    return [TestResult(name=name, status=status) for name, status in seen.items()]

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
