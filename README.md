# 🔍 TestLeak — Test Pollution Root-Cause Tracker

Stop debugging flaky tests blindly. TestLeak snapshots process state before/after **every test** and tells you exactly which test leaked what.

## 🚀 Quick Start

```bash
pip install testleak

# Just run your tests — TestLeak auto-activates
pytest

# Gate CI on pollution
pytest --testleak-fail

# Export JSON report
pytest --testleak-report pollution.json

# Or use the CLI
testleak scan tests/ --fail --report pollution.json
testleak show pollution.json
```

## 📸 Example Output

```
🚨 TestLeak: 3 leak(s) detected!

  📍 tests/test_auth.py::test_login_as_admin
     [env_added] DATABASE_URL: None → 'postgres://admin@localhost/prod'
     [env_changed] APP_ENV: 'test' → 'production'

  📍 tests/test_utils.py::test_monkey_patch_time
     [cwd_changed] cwd: '/app' → '/tmp'
```

## 🎯 What It Catches

| Pollution Type | Free | Pro |
|---|---|---|
| Environment variable leaks | ✅ | ✅ |
| `sys.path` mutations | ✅ | ✅ |
| Working directory changes | ✅ | ✅ |
| JSON report export | ✅ | ✅ |
| `--testleak-fail` CI gate | ✅ | ✅ |
| Pollution chain (A→B→C) | ❌ | ✅ |
| Auto-fix suggestions | ❌ | ✅ |
| `sys.modules` side-load tracking | ❌ | ✅ |
| Signal handler leak detection | ❌ | ✅ |
| DB record residue detection | ❌ | ✅ |
| GitHub PR comments | ❌ | ✅ |
| Slack/Teams alerts | ❌ | ✅ |
| SARIF output for code scanning | ❌ | ✅ |
| Priority support | ❌ | ✅ |

## 💰 Pricing

| Plan | Price | For |
|---|---|---|
| **Free** | $0 | Individual devs, open-source |
| **Pro** | $49/mo | Small teams, startups |
| **Team** | $99/mo | Up to 20 seats, CI integration |
| **Enterprise** | $199/mo | Unlimited seats, SSO, SLA |

## 📊 Why Pay?

- **Flaky tests cost $100k+/year** at mid-size companies (Google internal study: 16% of eng time)
- One pollution-caused outage in CI can block 50+ engineers for hours
- TestLeak Pro pays for itself after catching **one** flaky test root cause
- Fintech/healthtech compliance requires deterministic test suites

## 🔧 How It Works

1. `pytest_runtest_setup` — snapshot `os.environ`, `sys.path`, `os.getcwd()`
2. `pytest_runtest_teardown` — diff against snapshot
3. `pytest_terminal_summary` — report all leaks with test IDs
4. Zero overhead on clean tests (~0.1ms per test)

## License

MIT (Free tier) · Commercial license for Pro/Enterprise features
