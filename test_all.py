"""test_all.py: every test in the project, in one file.

Run everything:        python test_all.py
Run only your part:    python test_all.py gbn      (tests whose name starts with test_gbn)

Each section belongs to one person. Your tests fail until you write your
code; that is expected. Tests use small files and a 2 ms delay so they run fast.
"""

import sys
import time
import channel
import rto
from channel import Channel, damage
from rto import FixedRTO, AdaptiveRTO


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


def test_rto_adaptive():
    rto = AdaptiveRTO(initial=0.2, min_rto=0.05, max_rto=10.0)
    assert abs(rto.value() - 0.2) < 1e-6

    rto.sample(0.1, False)
    assert rto.srtt == 0.1
    assert rto.rttvar == 0.05
    assert abs(rto.value() - 0.3) < 1e-6

    rto.sample(0.2, True)
    assert rto.srtt == 0.1

    rto.backoff()
    assert abs(rto.value() - 0.6) < 1e-6

    rto.forward()
    assert abs(rto.value() - 0.3) < 1e-6


def test_rto_karn_toggle():
    rto = AdaptiveRTO(initial=0.2, karn=False)
    rto.sample(0.1, False)
    assert rto.srtt == 0.1
    rto.sample(0.2, True)
    assert rto.srtt != 0.1
    assert len(rto.trace) == 2


def test_channel_damage():
    ch = Channel(loss=1.0, seed=42)
    assert ch.damage(b"hello") == []

    ch_clean = Channel(loss=0.0, corrupt=0.0, dup=0.0, delay=0.0, seed=42)
    assert ch_clean.damage(b"hello") == [b"hello"]

    ch_dup = Channel(dup=1.0, seed=42)
    assert ch_dup.damage(b"hello") == [b"hello", b"hello"]

    ch_corrupt = Channel(corrupt=1.0, seed=42)
    damaged = ch_corrupt.damage(b"hello")
    assert len(damaged) == 1
    assert damaged[0] != b"hello"
    assert len(damaged[0]) == len(b"hello")


def test_channel_determinism():
    ch1 = Channel(loss=0.5, corrupt=0.2, seed=12345)
    ch2 = Channel(loss=0.5, corrupt=0.2, seed=12345)
    p1 = [ch1.damage(b"\x00\x00\x00\x01data") for _ in range(10)]
    p2 = [ch2.damage(b"\x00\x00\x00\x01data") for _ in range(10)]
    assert p1 == p2


def test_channel_rate_limit():
    ch = Channel(rate=10000, seed=42)
    ch.tokens = 0
    start = time.monotonic()
    ch.damage(b"a" * 100)
    elapsed = time.monotonic() - start
    assert elapsed >= 0.005


def run_tests():
    filter_name = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    tests = [
        ("test_rto_fixed", test_rto_fixed),
        ("test_rto_adaptive", test_rto_adaptive),
        ("test_rto_karn_toggle", test_rto_karn_toggle),
        ("test_channel_damage", test_channel_damage),
        ("test_channel_determinism", test_channel_determinism),
        ("test_channel_rate_limit", test_channel_rate_limit),
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
