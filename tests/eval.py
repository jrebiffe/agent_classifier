"""Tiny end-to-end eval harness (requires a real API key).

This is intentionally *not* a pytest test — it makes real model calls. Run it
manually once credentials are set:

    python tests/eval.py

Add more (fixture, expectations) entries to ``CASES`` to grow the labeled set.
Expectations are deliberately soft (membership / thresholds), since exact
wording will vary between model runs.
"""

import os
from pathlib import Path

from agent_classifier import build_agent, classify
from agent_classifier.taxonomy import Severity

FIXTURES = Path(__file__).parent / "fixtures"

_STRONG = {Severity.HIGH, Severity.CRITICAL}

# (name, source, expectation-checks). Each check is (label, callable(result)->bool).
CASES = [
    (
        "support-refund-agent",
        FIXTURES / "sample_agent",
        [
            (
                "domain is customer_support or finance",
                lambda r: r.domain in ("customer_support", "finance"),
            ),
            ("overall risk is high or critical", lambda r: r.overall_risk in _STRONG),
            (
                "flags a financial_transaction risk",
                lambda r: any(
                    risk.category == "financial_transaction" for risk in r.risks
                ),
            ),
            ("finds at least one goal", lambda r: len(r.goals) >= 1),
        ],
    ),
]


def main() -> int:
    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("AGENT_CLASSIFIER_MODEL")):
        print(
            "Set ANTHROPIC_API_KEY (and optionally AGENT_CLASSIFIER_MODEL) to run the eval."
        )
        return 1

    agent = build_agent()
    total = passed = 0
    for name, source, checks in CASES:
        print(f"\n=== {name} ===")
        result = classify(source, agent=agent)
        print(
            f"  domain={result.domain}  category={result.category}  "
            f"autonomy={result.autonomy_level}  overall_risk={result.overall_risk}  "
            f"confidence={result.confidence}"
        )
        print(f"  risks: {[r.category for r in result.risks]}")
        for label, check in checks:
            total += 1
            ok = bool(check(result))
            passed += ok
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")

    print(f"\n{passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
