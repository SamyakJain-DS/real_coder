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

# Map the verbose-mode keywords pytest prints next to each test id.
_STATUS_MAP = {
    "PASSED": TestStatus.PASSED,
    "FAILED": TestStatus.FAILED,
    "SKIPPED": TestStatus.SKIPPED,
    "ERROR": TestStatus.ERROR,
    "XFAIL": TestStatus.PASSED,
    "XPASS": TestStatus.PASSED,
    "XFAILED": TestStatus.PASSED,
    "XPASSED": TestStatus.PASSED,
}

# Lines look like: "tests/test_pipeline.py::test_name PASSED [ 12%]" or
# "/eval_assets/tests/test_pipeline.py::test_name FAILED".
_VERBOSE_RE = re.compile(
    r"^(?P<name>\S+::\S+?)\s+"
    r"(?P<status>PASSED|FAILED|ERROR|SKIPPED|XFAILED|XPASSED|XFAIL|XPASS)"
    r"(?:\s|$)"
)

# Short summary lines look like: "FAILED tests/test_pipeline.py::test_name - ..."
_SUMMARY_RE = re.compile(
    r"^(?P<status>PASSED|FAILED|ERROR|SKIPPED|XFAILED|XPASSED|XFAIL|XPASS)\s+"
    r"(?P<name>\S+::\S+)"
)


def _normalize_name(name: str) -> str:
    """Strip pytest parametrize trailing whitespace / odd characters."""
    return name.strip()


def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Parse the test output content and extract test results.

    Reads pytest's verbose per-test status lines as well as the short
    summary block. Later observations of a given test override earlier
    ones, so the short summary (printed last) is authoritative when
    available.
    """
    seen = {}
    combined = (stdout_content or "") + "\n" + (stderr_content or "")

    for raw in combined.splitlines():
        line = raw.strip()
        if not line:
            continue

        m = _VERBOSE_RE.match(line)
        if m:
            seen[_normalize_name(m.group("name"))] = _STATUS_MAP.get(
                m.group("status"), TestStatus.FAILED
            )
            continue

        m = _SUMMARY_RE.match(line)
        if m:
            seen[_normalize_name(m.group("name"))] = _STATUS_MAP.get(
                m.group("status"), TestStatus.FAILED
            )

    return [TestResult(name=n, status=s) for n, s in seen.items()]

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
