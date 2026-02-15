"""TestLeak pytest plugin — detect test pollution automatically."""
import os
import sys
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

IGNORED_ENV_KEYS = frozenset({"PYTEST_CURRENT_TEST"})


@dataclass
class Leak:
    test_id: str
    category: str
    key: str
    before: Any = None
    after: Any = None


class PollutionTracker:
    def __init__(self):
        self.leaks: List[Leak] = []
        self._env: Optional[Dict[str, str]] = None
        self._paths: Optional[List[str]] = None
        self._cwd: Optional[str] = None

    def snapshot(self):
        self._env = dict(os.environ)
        self._paths = list(sys.path)
        self._cwd = os.getcwd()

    def diff(self, test_id: str):
        if self._env is None:
            return
        now_env = dict(os.environ)
        for k, v in now_env.items():
            if k in IGNORED_ENV_KEYS:
                continue
            if k not in self._env:
                self.leaks.append(Leak(test_id, "env_added", k, after=v))
            elif self._env[k] != v:
                self.leaks.append(Leak(test_id, "env_changed", k, self._env[k], v))
        for k in self._env:
            if k not in now_env and k not in IGNORED_ENV_KEYS:
                self.leaks.append(Leak(test_id, "env_removed", k, before=self._env[k]))
        for p in sys.path:
            if p not in self._paths:
                self.leaks.append(Leak(test_id, "sys_path_added", p))
        cwd_now = os.getcwd()
        if cwd_now != self._cwd:
            self.leaks.append(Leak(test_id, "cwd_changed", "cwd", self._cwd, cwd_now))

    def to_json(self) -> str:
        return json.dumps([asdict(l) for l in self.leaks], indent=2, default=str)


_tracker = PollutionTracker()


def pytest_addoption(parser):
    grp = parser.getgroup("testleak", "Test pollution detection")
    grp.addoption("--testleak-report", default=None, help="Write JSON report")
    grp.addoption("--testleak-fail", action="store_true", default=False, help="Fail on leaks")


def pytest_runtest_setup(item):
    _tracker.snapshot()


def pytest_runtest_teardown(item, nextitem):
    _tracker.diff(item.nodeid)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not _tracker.leaks:
        terminalreporter.write_line("\n\u2705 TestLeak: No test pollution detected!", green=True)
        return
    n = len(_tracker.leaks)
    terminalreporter.write_line(f"\n\U0001f6a8 TestLeak: {n} leak(s) detected!", red=True)
    by_test: Dict[str, List[Leak]] = {}
    for leak in _tracker.leaks:
        by_test.setdefault(leak.test_id, []).append(leak)
    for tid, leaks in by_test.items():
        terminalreporter.write_line(f"\n  \U0001f4cd {tid}", yellow=True)
        for lk in leaks:
            terminalreporter.write_line(
                f"     [{lk.category}] {lk.key}: {lk.before!r} -> {lk.after!r}"
            )
    report_path = config.getoption("--testleak-report", default=None)
    if report_path:
        Path(report_path).write_text(_tracker.to_json())
        terminalreporter.write_line(f"\n\U0001f4c4 Report written to {report_path}")


def pytest_sessionfinish(session, exitstatus):
    if session.config.getoption("--testleak-fail", default=False) and _tracker.leaks:
        session.exitstatus = 1
