"""channel.py: the middleman that damages traffic on purpose. Owner: Archit.

The sender and receiver never talk directly. Every packet goes through the
channel, which decides what happens to it: dropped, corrupted, duplicated,
delayed, or held back so later packets overtake it.

Each direction has its own random generator built from the seed, so the
same seed makes the same decisions for the same packets.
"""

import random
import time


class Channel:
    def __init__(self, loss=0.0, corrupt=0.0, dup=0.0, delay=0.0, jitter=0.0, reorder=0.0, seed=None):
        self.loss = loss
        self.corrupt = corrupt
        self.dup = dup
        self.delay = delay
        self.jitter = jitter
        self.reorder = reorder
        self.rng = random.Random(seed)
        self.held = None

    def damage(self, data):
        if not data:
            return []

        if self.loss > 0 and self.rng.random() < self.loss:
            return []

        pkt = bytearray(data)
        if self.corrupt > 0 and len(pkt) > 0 and self.rng.random() < self.corrupt:
            idx = self.rng.randint(0, len(pkt) - 1)
            pkt[idx] ^= 0xFF

        res = [bytes(pkt)]
        if self.dup > 0 and self.rng.random() < self.dup:
            res.append(bytes(pkt))

        if self.delay > 0:
            d = self.delay
            if self.jitter > 0:
                d += self.rng.uniform(-self.jitter, self.jitter)
            if d > 0:
                time.sleep(d)

        if self.reorder > 0 and self.rng.random() < self.reorder:
            if self.held is None:
                self.held = res
                return []
            else:
                out = res + self.held
                self.held = None
                return out
        elif self.held is not None:
            out = res + self.held
            self.held = None
            return out

        return res


def damage(data, loss=0.0, corrupt=0.0, dup=0.0, delay=0.0, jitter=0.0, reorder=0.0, seed=None):
    c = Channel(loss=loss, corrupt=corrupt, dup=dup, delay=delay, jitter=jitter, reorder=reorder, seed=seed)
    return c.damage(data)


