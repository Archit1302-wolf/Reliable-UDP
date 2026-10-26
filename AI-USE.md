# AI use

Course rule: no AI writes core logic. Core functions are written by their owner.
The stubs hold only signatures and the shared interface.

Core: packet.py (top half), stopwait.py, gbn.py, sr.py, channel.py (damage),
rto.py (the two classes).

## Atul
- Used AI for building `test_all.py` test suite code to review and verify whether my code was working properly.

## Shashank

## Aqifa

## Archit
- Used AI for building test_all.py unit tests for FixedRTO and channel damage logic.
- Used AI to formulate RFC 6298 first-sample and variance-tracking unit tests for AdaptiveRTO (Oct 12 milestone).
- Used AI to validate Karn's algorithm RTT ambiguity edge cases and trace schema tests (Oct 13 milestone).
- Used AI to design determinism verification tests and hash-seeded attempt tracking tests (Oct 14 milestone).
- Used AI to formulate token bucket burst capacity and throttling edge tests (Oct 15 milestone).
- Used AI to build end-to-end channel integration tests with composite impairments and reordering recovery (Oct 16 milestone).
- Used AI to build determinism drill verification tests and userspace netem emulation documentation (Oct 17 milestone).
- Used AI to formulate boundary invariance tests and variable-payload corruption checks (Oct 19 milestone).
- Used AI to assist in reviewing Shashank's GBN PR #4 (rto interface verification) and formulating scratch.py practice helper functions (Oct 19 milestone).
- Used AI to formulate Karn's algorithm hand-trace simulation and rto_after verification logic (Oct 20 milestone).
- Used AI to verify Checkpoint 2 test suite and align channel.damage signature (Oct 21 milestone).
- Recorded official Code Freeze validation: 36 passed on Python 3.14 win32 environment (Oct 22 milestone).
- Formulated mean_goodput statistical extractor and documented Plot 4/Plot 5 analysis (Oct 23 milestone).
- Formulated draft of Report Section 2.4 (Channel impairment pipeline and RFC 6298 adaptive RTO) (Oct 24 milestone).

## Harsha
