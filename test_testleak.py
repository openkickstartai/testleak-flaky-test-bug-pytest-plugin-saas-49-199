"""Tests for TestLeak pollution tracker core logic."""
import json
import os
import sys

from testleak_plugin import PollutionTracker


class TestEnvVarDetection:
    def test_detects_added_env_var(self):
        t = PollutionTracker()
        t.snapshot()
        os.environ["_TL_TEST_ADD"] = "leaked"
        t.diff("tests/demo.py::test_leaker")
        del os.environ["_TL_TEST_ADD"]
        assert len(t.leaks) == 1
        assert t.leaks[0].category == "env_added"
        assert t.leaks[0].key == "_TL_TEST_ADD"
        assert t.leaks[0].after == "leaked"

    def test_detects_changed_env_var(self):
        os.environ["_TL_TEST_CHG"] = "old"
        t = PollutionTracker()
        t.snapshot()
        os.environ["_TL_TEST_CHG"] = "new"
        t.diff("tests/demo.py::test_mutator")
        del os.environ["_TL_TEST_CHG"]
        assert len(t.leaks) == 1
        assert t.leaks[0].category == "env_changed"
        assert t.leaks[0].before == "old"
        assert t.leaks[0].after == "new"

    def test_detects_removed_env_var(self):
        os.environ["_TL_TEST_DEL"] = "present"
        t = PollutionTracker()
        t.snapshot()
        del os.environ["_TL_TEST_DEL"]
        t.diff("tests/demo.py::test_deleter")
        assert len(t.leaks) == 1
        assert t.leaks[0].category == "env_removed"
        assert t.leaks[0].before == "present"


class TestSysPathDetection:
    def test_detects_sys_path_addition(self):
        t = PollutionTracker()
        t.snapshot()
        fake = "/testleak/fake/injected/path"
        sys.path.insert(0, fake)
        t.diff("tests/demo.py::test_path_polluter")
        sys.path.remove(fake)
        path_leaks = [lk for lk in t.leaks if lk.category == "sys_path_added"]
        assert len(path_leaks) == 1
        assert path_leaks[0].key == fake


class TestCwdDetection:
    def test_detects_cwd_change(self):
        original = os.getcwd()
        t = PollutionTracker()
        t.snapshot()
        os.chdir("/tmp")
        t.diff("tests/demo.py::test_chdir")
        os.chdir(original)
        cwd_leaks = [lk for lk in t.leaks if lk.category == "cwd_changed"]
        assert len(cwd_leaks) == 1
        assert cwd_leaks[0].after == "/tmp"


class TestCleanBehavior:
    def test_no_false_positives(self):
        t = PollutionTracker()
        t.snapshot()
        _ = sum(range(1000))
        t.diff("tests/demo.py::test_clean")
        assert len(t.leaks) == 0

    def test_json_export(self):
        t = PollutionTracker()
        t.snapshot()
        os.environ["_TL_TEST_JSON"] = "val"
        t.diff("tests/demo.py::test_json")
        del os.environ["_TL_TEST_JSON"]
        data = json.loads(t.to_json())
        assert len(data) == 1
        assert data[0]["category"] == "env_added"
        assert data[0]["test_id"] == "tests/demo.py::test_json"
