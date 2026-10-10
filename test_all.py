"""test_all.py: every test in the project, in one file.

Run everything:        python test_all.py
Run only your part:    python test_all.py gbn      (tests whose name starts with test_gbn)

Each section belongs to one person. Your tests fail until you write your
code; that is expected. Tests use small files and a 2 ms delay so they run fast.
"""

import sys
import time
from rto import FixedRTO


# --- Archit: rto.py & channel.py ---
def test_rto_fixed():
    rto = FixedRTO(0.2)
    assert abs(rto.value() - 0.2) < 1e-6
    rto.sample(0.05, False)
    assert abs(rto.value() - 0.2) < 1e-6
    rto.backoff()
    assert abs(rto.value() - 0.4) < 1e-6
    rto.forward()
    assert abs(rto.value() - 0.2) < 1e-6


def run_tests():
    filter_name = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    tests = [
        ("test_rto_fixed", test_rto_fixed),
    ]

    passed = 0
    total = 0
    for name, fn in tests:
        if filter_name and filter_name not in name.lower():
            continue
        total += 1
        try:
            fn()
            print(f"[PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")

    print(f"\n{passed}/{total} tests passed.")


if __name__ == "__main__":
    run_tests()
