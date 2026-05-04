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

_RESULT_PATTERN = re.compile(r"^(PASSED|FAILED|SKIPPED|ERROR)\s+(.+)$")

# Pytest's verbose reporter prints one line per test of the form
#   <nodeid> <STATUS> [ pct%]
# where <nodeid> is e.g. "tests/test_embeddable_webdav.py::test_t001_xyz".
# The trailing "[ pct%]" suffix is optional (e.g. when only one test
# is collected the percentage column is sometimes omitted on resumed
# runs). We accept it either way so the parser remains tolerant of
# slight formatting variations between pytest versions.
_PYTEST_PATTERN = re.compile(
    r"^(?P<name>\S.*?)\s+(?P<status>PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)"
    r"(?:\s+\[\s*\d+%\s*\])?\s*$"
)

_PYTEST_STATUS_MAP = {
    "PASSED": TestStatus.PASSED,
    "XPASS": TestStatus.PASSED,
    "FAILED": TestStatus.FAILED,
    "ERROR": TestStatus.ERROR,
    "SKIPPED": TestStatus.SKIPPED,
    "XFAIL": TestStatus.SKIPPED,
}


def _parse_pytest_verbose(stdout_content: str) -> List[TestResult]:
    """Parse pytest's `--reporter=verbose` output (one status per test).

    Each per-test line looks like::

        tests/test_embeddable_webdav.py::test_t001_xyz PASSED [  1%]

    Section banners and traceback text are filtered out by requiring the
    line to contain a recognised status token in the expected position.
    Returns an empty list when no per-test lines were found so the caller
    can fall back to a different parser.
    """
    results: List[TestResult] = []
    for line in stdout_content.splitlines():
        stripped = line.rstrip()
        if not stripped:
            continue
        match = _PYTEST_PATTERN.match(stripped)
        if not match:
            continue
        name = match.group("name").strip()
        # Reject banner-style "STATUS message" lines and pytest's summary
        # blocks (e.g. "FAILED tests/test_x.py::test_y - AssertionError"),
        # neither of which represents a per-test status row.
        if not name or name.startswith(("=", "-", "_")):
            continue
        if "::" not in name:
            continue
        status = _PYTEST_STATUS_MAP.get(match.group("status"), TestStatus.FAILED)
        results.append(TestResult(name=name, status=status))
    return results


def _parse_status_lines(stdout_content: str) -> List[TestResult]:
    """Parse '<STATUS> <name>' lines (legacy pytest-style verbose output)."""
    results: List[TestResult] = []
    for line in stdout_content.splitlines():
        match = _RESULT_PATTERN.match(line)
        if match:
            status_str, name = match.groups()
            status = (
                TestStatus.PASSED
                if status_str == "PASSED"
                else TestStatus.FAILED
            )
            results.append(TestResult(name=name.strip(), status=status))
    return results


def parse_test_output(
    stdout_content: str, stderr_content: str
) -> List[TestResult]:
    """Parse captured pytest stdout into a list of TestResult.

    Two input formats are supported:

      1. Pytest's verbose reporter ('<nodeid> <STATUS> [pct%]'). This is
         what the project's run.sh emits today.
      2. '<STATUS> <name>' lines, retained for backwards compatibility
         with prior run.sh variants that post-processed pytest output.

    The verbose-reporter parser runs first; if zero per-test rows match,
    the line-based parser runs as a fallback.
    """
    # Tolerate an optional UTF-8 BOM at the start of the captured stdout.
    # On Linux (the production runtime) Python's default encoding is UTF-8
    # and the BOM decodes as a single '\ufeff' character. On Windows the
    # default encoding is cp1252 and the same three BOM bytes (ef bb bf)
    # decode as the mojibake sequence 'ï»¿'. Strip either form.
    if stdout_content.startswith("\ufeff"):
        stdout_content = stdout_content[1:]
    elif stdout_content.startswith("\u00ef\u00bb\u00bf"):
        stdout_content = stdout_content[3:]
    results = _parse_pytest_verbose(stdout_content)
    if results:
        return results
    return _parse_status_lines(stdout_content)


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