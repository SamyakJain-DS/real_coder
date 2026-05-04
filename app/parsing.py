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
 
def parse_test_output(stdout_content: str, stderr_content: str) -> List[TestResult]:
    """
    Parse Vitest --reporter=verbose output and extract individual test results.
    """
    import re
 
    # Strip ANSI colour codes that Vitest emits in verbose mode.
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
 
    # Match lines that begin with a Vitest status symbol followed by a name.
    # Note: Vitest uses both '>' (U+003E) and '›' (U+203A, single right-pointing
    # angle quotation mark) as the suite-separator character depending on
    # version. Both are handled in is_individual_test() below.
    symbol_pattern = re.compile(r'^\s*([✓×✗↓])\s+(.+?)\s*$', re.MULTILINE)
 
    # Match lines that begin with a WORD status (PASS/FAIL/…).
    word_pattern = re.compile(r'^\s*(PASS|FAIL|FAILED|ERROR|SKIP|SKIPPED)\s+(.+?)\s*$', re.MULTILINE)
 
    # Fallback: match suite-level FAIL lines when no individual tests parsed.
    suite_fail_pattern = re.compile(
        r'^\s*FAIL\s+(.+?\.(?:test|spec)\.[cm]?[jt]sx?)\s+\[\s*(.+?)\s*\]\s*$',
        re.MULTILINE,
    )
 
    # Strip trailing duration stamps ("4ms", "1.2s") and summary suffixes.
    duration_pattern = re.compile(r'\s+\d+(?:\.\d+)?\s*(?:ms|s)$')
    file_summary_pattern = re.compile(r'\(\s*\d+\s+(?:tests?|skipped|failed|passed)\s*\)')
 
    status_map = {
        '✓': TestStatus.PASSED,
        '×': TestStatus.FAILED,
        '✗': TestStatus.FAILED,
        '↓': TestStatus.SKIPPED,
        'PASS':    TestStatus.PASSED,
        'FAIL':    TestStatus.FAILED,
        'PASSED':  TestStatus.PASSED,
        'FAILED':  TestStatus.FAILED,
        'ERROR':   TestStatus.ERROR,
        'SKIP':    TestStatus.SKIPPED,
        'SKIPPED': TestStatus.SKIPPED,
    }
 
    # Precedence for deduplication: higher wins when the same test appears
    # multiple times (e.g., retried or restated in summary).
    precedence = {
        TestStatus.PASSED:  0,
        TestStatus.SKIPPED: 1,
        TestStatus.FAILED:  2,
        TestStatus.ERROR:   3,
    }
 
    ordered_names: List[str] = []
    results_by_name: dict = {}
 
    def record(name: str, status: TestStatus) -> None:
        if name not in results_by_name:
            ordered_names.append(name)
            results_by_name[name] = status
            return
        if precedence[status] > precedence[results_by_name[name]]:
            results_by_name[name] = status
 
    def clean_test_name(name: str) -> str:
        name = duration_pattern.sub('', name).strip()
        name = re.sub(r'\s+\(.+?\)$', '', name).strip()
        return name
 
    def is_individual_test(name: str) -> bool:
        """
        Return True only for individual test lines, not for file/suite summaries.
 
        Vitest verbose output uses ' > ' (ASCII >) as the suite separator on
        most versions and ' › ' (U+203A) on some older/variant builds. Both
        are checked so the parser is robust across Vitest releases. The '::'
        separator is included for compatibility with other test frameworks.
        """
        if file_summary_pattern.search(name):
            return False
        return ' > ' in name or ' \u203a ' in name or '::' in name
 
    combined = f'{stdout_content}\n{stderr_content}'
 
    for raw_line in combined.splitlines():
        line = ansi_escape.sub('', raw_line).strip()
        if not line:
            continue
 
        # Symbol-prefixed individual test lines (primary path for Vitest verbose).
        m = symbol_pattern.match(line)
        if m:
            symbol = m.group(1)
            test_name = clean_test_name(m.group(2).strip())
            if is_individual_test(test_name) and symbol in status_map:
                record(test_name, status_map[symbol])
            continue
 
        # Word-prefixed lines (PASS/FAIL/… — secondary path).
        m = word_pattern.match(line)
        if m:
            status_word = m.group(1)
            test_name = clean_test_name(m.group(2).strip())
            if is_individual_test(test_name):
                record(test_name, status_map[status_word])
            continue
 
    # Fallback: if nothing was parsed, try to surface suite-level failures.
    if not ordered_names:
        for m in suite_fail_pattern.finditer(ansi_escape.sub('', combined)):
            file_name = m.group(1).strip()
            suite_name = m.group(2).strip()
            record(f'{file_name} > {suite_name}', TestStatus.FAILED)
 
    # Last-resort fallback: record a single ERROR entry so before.json /
    # after.json are never silently empty when the test run crashes entirely.
    if not ordered_names and ('ERROR:' in combined or 'Error:' in combined):
        record('Test run', TestStatus.ERROR)
 
    return [TestResult(name=n, status=results_by_name[n]) for n in ordered_names]
 
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