# Plot 4 & Plot 5 Analysis (Oct 23 Milestone)

## 1. Plot 4: RTO Policy at 5% Loss, Window = 32

### Mean Goodput Summary (Mbps)
| Protocol | Adaptive | Adaptive-NoKarn | Fixed:0.5 | Speedup (Adaptive / Fixed) |
| :--- | :--- | :--- | :--- | :--- |
| **Selective Repeat (SR)** | **2.77** | 2.71 | **0.53** | **5.2x** |
| **Go-Back-N (GBN)** | **1.26** | 1.25 | **0.28** | **4.5x** |

### Key Observations
1. **The Cost of Fixed Waiting**: `fixed:0.5` causes dramatic throughput degradation across both protocols (~5.2x penalty for SR, ~4.5x for GBN). A fixed 500 ms timeout forces every loss recovery to wait approximately 10 round trips (~50 ms RTT baseline), leaving the pipeline severely underutilized.
2. **Karn's Rule Impact on Bulk Goodput**: Karn's rule ON vs OFF yields nearly identical bulk goodput (within ~2% for SR, <1% for GBN). Under standard independent losses, ambiguous samples are infrequent enough not to derail goodput, but Karn's rule preserves estimator stability.

---

## 2. Plot 5: RTO Trace vs. Measured RTT (SR, W=32, 5% Loss, Seed 1)

### Sample Metrics
| Policy | Total Valid Samples | Mean Measured RTT | Mean RTO Estimate | Max RTO Spike |
| :--- | :--- | :--- | :--- | :--- |
| **Adaptive (Karn ON)** | 927 | 48.9 ms | 61.0 ms | 117.1 ms |
| **Adaptive-NoKarn (Karn OFF)** | 1024 | 48.6 ms | 61.7 ms | 122.5 ms |

### Graphical Dynamics
1. **Estimate Tracking**: The RTO line rides consistently ~12.1 ms above the cloud of RTT dots. This ~12 ms margin corresponds to $4 \times \text{RTTVAR}$, keeping the timer tight to avoid false timeouts while providing sufficient headroom.
2. **Spike Etiology**: Sharp vertical spikes in the RTO curve occur during loss events where exponential backoff doubles the timer. Once an ACK arrives advancing the window, `forward()` immediately restores the base estimate.
3. **Sample Count Divergence**: Karn ON records 927 samples compared to 1024 with Karn OFF. The difference (97 discarded samples) represents ACKs for retransmitted packets correctly rejected by Karn's rule to eliminate RTT ambiguity.
