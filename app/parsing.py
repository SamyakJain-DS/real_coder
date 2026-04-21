#!/usr/bin/env python3
import dataclasses
import json
import re
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
    Parse TAP output from `node --test` and extract individual test results.

    Each 'ok' / 'not ok' line may be followed by an indented YAML block
    (bounded by '---' and '...') that describes the failure. We use that
    block to distinguish tests that ERRORED (e.g. a source module could
    not be loaded) from tests that actually FAILED an assertion.
    """
    results = []
    seen = set()

    lines = stdout_content.splitlines()
    test_line = re.compile(r'^\s*(ok|not ok)\s+\d+\s+-\s+(.+?)\s*$')
    yaml_open = re.compile(r'^\s*---\s*$')
    yaml_close = re.compile(r'^\s*\.\.\.\s*$')

    # Patterns that indicate the test could not actually run
    # (source module missing, import failure, environment missing, etc.)
    load_failure_markers = (
        'could not be loaded',
        'cannot find module',
        'cannot find package',
        'module not found',
        'err_module_not_found',
        'failed to resolve module',
    )

    def classify_not_ok(yaml_text: str) -> TestStatus:
        lowered = yaml_text.lower()
        for marker in load_failure_markers:
            if marker in lowered:
                return TestStatus.ERROR

        failure_type = _yaml_string_field(yaml_text, 'failureType')
        error_name = _yaml_string_field(yaml_text, 'name')

        # Hook failures, cancellations, and top-level runtime errors
        # are environmental/structural problems, not assertion failures.
        if failure_type and failure_type not in (
            'testCodeFailure',
            'testTimeoutFailure',
            'subtestsFailed',
        ):
            return TestStatus.ERROR

        # If the thrown value is not an AssertionError, treat it as an
        # unexpected runtime error instead of a normal assertion failure.
        non_assertion_errors = (
            'TypeError',
            'ReferenceError',
            'SyntaxError',
            'RangeError',
            'URIError',
            'EvalError',
        )
        if error_name in non_assertion_errors:
            return TestStatus.ERROR

        return TestStatus.FAILED

    i = 0
    while i < len(lines):
        m = test_line.match(lines[i])
        if not m:
            i += 1
            continue

        status_str = m.group(1)
        name = m.group(2).strip()

        # Walk any YAML block attached to this entry so we can inspect it
        # and also so the outer loop does not re-parse lines inside it.
        yaml_buf = []
        j = i + 1
        if j < len(lines) and yaml_open.match(lines[j]):
            j += 1
            while j < len(lines) and not yaml_close.match(lines[j]):
                yaml_buf.append(lines[j])
                j += 1
            if j < len(lines):
                j += 1
        yaml_text = '\n'.join(yaml_buf)
        i = j

        # Skip file-level entries (name ends in a test-file filename).
        if name.endswith('.mjs') or name.endswith('.js'):
            continue

        skip_match = re.search(r'\s*#\s*SKIP\b', name, re.IGNORECASE)
        if skip_match:
            name = name[:skip_match.start()].strip()
            status = TestStatus.SKIPPED
        elif status_str == 'ok':
            status = TestStatus.PASSED
        else:
            status = classify_not_ok(yaml_text)

        if name and name not in seen:
            seen.add(name)
            results.append(TestResult(name=name, status=status))

    return results


def _yaml_string_field(yaml_text: str, field: str) -> str:
    """
    Extract a single-line string value for `field:` out of a small TAP
    YAML block. Supports both quoted and unquoted forms. Returns '' when
    the field is absent.
    """
    pattern = re.compile(
        r"^\s*" + re.escape(field) + r":\s*(?:'([^']*)'|\"([^\"]*)\"|(.+?))\s*$",
        re.MULTILINE,
    )
    m = pattern.search(yaml_text)
    if not m:
        return ''
    return (m.group(1) or m.group(2) or m.group(3) or '').strip()

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
