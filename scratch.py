"""scratch.py: Daily viva practice and experimental helper functions for Archit.

Contains:
- Tue 13 Oct: backoff_steps (exponential backoff progression)
- Wed 14 Oct: dropped (channel seed determinism check)
- Thu 15 Oct: send_times (FIFO queue send times with reorder hold-back)
- Fri 16 Oct: differs (comparing experiment JSON rows across seeds)
- Sat 17 Oct: goodput (goodput calculation in Mbps)
"""

from typing import List, Tuple, Dict, Any


def backoff_steps(base_ms: float, timeouts: int, cap_ms: float) -> List[float]:
    """Calculate the RTO after each consecutive timeout, up to a cap.

    Args:
        base_ms: The RTO before any timeout.
        timeouts: How many timers run out in a row.
        cap_ms: The largest wait allowed.

    Returns:
        A list of RTO values after each timeout in ms.
    """
    multiplier = 1.0
    steps = []
    for _ in range(timeouts):
        if base_ms * multiplier < cap_ms:
            multiplier *= 2.0
        val = min(base_ms * multiplier, cap_ms)
        steps.append(val)
    return steps


def dropped(seed: int, loss: float, n: int) -> List[bool]:
    """Return, for each of the first n DATA packets, True if the channel drops it.

    In the channel model, a kept packet consumes 5 random draws:
    (loss, corrupt, dup, jitter, reorder), while a dropped packet consumes 1 draw (loss).
    The DATA direction uses random.Random(seed * 2).

    Args:
        seed: Random seed for the channel.
        loss: Packet drop probability [0.0, 1.0].
        n: Number of packets to test.

    Returns:
        List of booleans where True indicates dropped.
    """
    import random
    rng = random.Random(seed * 2 if seed is not None else None)
    result = []
    for _ in range(n):
        loss_draw = rng.random()
        is_drop = loss_draw < loss
        result.append(is_drop)
        if not is_drop:
            # 4 subsequent draws: corrupt, dup, jitter, reorder
            for _ in range(4):
                rng.random()
    return result


def send_times(arrivals: List[Tuple[float, float]], limit_ms: float) -> List[float]:
    """Simulate FIFO channel queuing and reordering hold.

    Args:
        arrivals: List of (time_ms, delay_ms) in order of arrival.
        limit_ms: Normal delay limit (delay + jitter). Delays exceeding limit_ms
                  are intentional reorder holds.

    Returns:
        Send time of each packet copy in ms.
    """
    result = []
    last_normal = 0.0
    for arrival_time, delay in arrivals:
        send_time = arrival_time + delay
        if delay <= limit_ms:
            send_time = max(send_time, last_normal)
            last_normal = send_time
        result.append(send_time)
    return result


def differs(rows: List[Dict[str, Any]]) -> List[str]:
    """Find the keys whose values differ between rows.

    Args:
        rows: List of dictionary records (e.g. JSON rows from transfer.py).

    Returns:
        List of key names where values are not identical across all rows.
    """
    if not rows:
        return []
    keys = list(rows[0].keys())
    return [k for k in keys if any(r.get(k) != rows[0].get(k) for r in rows[1:])]


def goodput(size_bytes: int, seconds: float) -> float:
    """Calculate goodput in Megabits per second (Mbps).

    Args:
        size_bytes: Total data transferred in bytes.
        seconds: Elapsed transfer duration in seconds.

    Returns:
        Goodput in Mbps rounded to 4 decimal places.
    """
    if seconds <= 0:
        return 0.0
    return round((size_bytes * 8) / (seconds * 1_000_000), 4)


def rto_after(samples: List[Tuple[float, bool]], karn: bool) -> float:
    """Calculate final RTO in ms after a sequence of (rtt_ms, resent) samples.

    Args:
        samples: List of (rtt_ms, resent) pairs.
        karn: True to enable Karn's rule (ignoring resent samples).

    Returns:
        Final RTO in milliseconds rounded to 1 decimal place.
    """
    from rto import AdaptiveRTO
    rto = AdaptiveRTO(initial=1.0, min_rto=0.01, max_rto=60.0, karn=karn)
    for rtt_ms, resent in samples:
        rto.sample(rtt_ms / 1000.0, resent)
    return round(rto.value() * 1000.0, 1)


if __name__ == "__main__":
    # Tue 13 Oct verification
    b_steps = backoff_steps(120.0, 5, 1000.0)
    print("backoff_steps(120.0, 5, 1000.0):", b_steps)
    assert b_steps == [240.0, 480.0, 960.0, 1000.0, 1000.0]

    # Wed 14 Oct verification
    d_list = dropped(5, 0.3, 10)
    print("dropped(5, 0.3, 10):", d_list)
    assert d_list == [False, False, True, False, False, False, False, False, False, True]

    # Thu 15 Oct verification
    s_times = send_times([(0, 24), (1, 16), (2, 51), (3, 19)], 25)
    print("send_times([(0, 24), (1, 16), (2, 51), (3, 19)], 25):", s_times)
    assert s_times == [24, 24, 53, 24]

    # Fri 16 Oct verification
    diff_keys = differs([{"dropped": 12, "seconds": 3.1}, {"dropped": 12, "seconds": 3.4}])
    print("differs keys:", diff_keys)
    assert diff_keys == ["seconds"]

    # Sat 17 Oct verification
    gp1 = goodput(262144, 12.27)
    gp2 = goodput(262144, 21.78)
    print("goodput adaptive:", gp1, "fixed:0.5:", gp2)
    assert gp1 == 0.1709
    assert gp2 == 0.0963

    # Tue 20 Oct verification: Karn's rule
    rto_karn_on = rto_after([(40, False), (500, True)], True)
    rto_karn_off = rto_after([(40, False), (500, True)], False)
    print("rto_after with Karn ON:", rto_karn_on, "OFF:", rto_karn_off)
    assert rto_karn_on == 120.0
    assert rto_karn_off == 617.5

    print("\nAll scratch.py checks through Oct 20 PASS!")

