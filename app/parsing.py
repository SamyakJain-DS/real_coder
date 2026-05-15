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
    Parse vitest JSON reporter output and return one TestResult per assertion.
 
    run.sh runs vitest with --reporter=verbose --reporter=json:
    - verbose output  -> stdout  (human-readable, streaming as tests execute)
    - json output     -> stdout  (single blob appended at the end)
 
    The JSON blob always starts with {"numTotalTestSuites" (vitest's fixed key
    order). Anchoring on that literal avoids any false match on '{' characters
    that may appear in verbose progress lines or test names.
 
    Test name format:  <relative-file-path>::<fullName>
    e.g.  tests/mount.test.tsx::Requirement 5: App default export > ...
    """
    results: List[TestResult] = []
    json_data = None
 
    status_map = {
        'passed':  TestStatus.PASSED,
        'failed':  TestStatus.FAILED,
        'pending': TestStatus.SKIPPED,
        'skipped': TestStatus.SKIPPED,
        'todo':    TestStatus.SKIPPED,
    }
 
    # Search stdout first, then stderr as a fallback.
    for content in (stdout_content, stderr_content):
        idx = content.find('{"numTotalTestSuites"')
        if idx == -1:
            continue
        try:
            parsed = json.loads(content[idx:])
            if isinstance(parsed, dict) and 'testResults' in parsed:
                json_data = parsed
                break
        except (json.JSONDecodeError, ValueError):
            continue
 
    if not json_data:
        return results
 
    for suite in json_data.get('testResults', []):
        raw_path = suite.get('testFilePath') or suite.get('name', '')
        # Strip container-specific prefix so names are environment-portable.
        for prefix in ('/eval_assets/', '/app/'):
            if raw_path.startswith(prefix):
                raw_path = raw_path[len(prefix):]
                break
 
        for assertion in suite.get('assertionResults', []):
            full_name = (assertion.get('fullName') or '').strip()
            if not full_name:
                ancestors = assertion.get('ancestorTitles') or []
                title = assertion.get('title') or ''
                parts = list(ancestors) + ([title] if title else [])
                full_name = ' > '.join(parts)
 
            raw_status = (assertion.get('status') or 'failed').lower()
            status = status_map.get(raw_status, TestStatus.FAILED)
 
            results.append(TestResult(
                name=f"{raw_path}::{full_name}",
                status=status,
            ))
 
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