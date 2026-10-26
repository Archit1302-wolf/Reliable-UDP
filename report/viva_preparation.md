# Practice Viva Preparation Guide (Oct 27 Milestone)

## 1. Architecture of Harsha's `experiments.py` and `plots.py`

### Sweep Matrix & Experiment Runner (`configs()`)
Harsha's experiment harness generates **46 distinct configurations** across 4 parametric sweeps, evaluated across **3 independent seeds (1, 2, 3)** for a total of **138 experimental jobs**:

| Sweep | Evaluated Protocols | Sweep Parameter Values | Configurations | Total Jobs (x 3 seeds) |
| :--- | :--- | :--- | :--- | :--- |
| **Loss Sweep** | Stop-and-Wait, Go-Back-N, Selective Repeat | `loss` $\in \{0.0, 0.01, 0.02, 0.05, 0.1, 0.2\}$ | 3 x 6 = **18** | **54** |
| **Window Sweep** | Go-Back-N, Selective Repeat | `window` $\in \{1, 4, 16, 32, 64, 128\}$ | 2 x 6 = **12** | **36** |
| **Reorder Sweep** | Go-Back-N, Selective Repeat | `reorder` $\in \{0.0, 0.01, 0.05, 0.1, 0.2\}$ | 2 x 5 = **10** | **30** |
| **RTO Policy Sweep**| Go-Back-N, Selective Repeat | `rto` $\in \{\text{fixed:0.5}, \text{adaptive}, \text{adaptive-nokarn}\}$ | 2 x 3 = **6** | **18** |
| **TOTAL** | | | **46** | **138** |

### Execution Pipeline (`run_one` and `claim`)
1. **`run_one(cfg, seed, data)`**: Executes an isolated file transfer via `transfer.py`, collects transport statistics and socket instrumentation into a 17-column dictionary, and streams it to `results.csv`.
2. **`plots.py` (`load`)**: Ingests `results.csv`, filters out any aborted or corrupt transfers (`sha256_ok == True`), computes seed-averaged metrics, and exports plots 1 through 5.
3. **`claim(df)`**: Evaluates 4 programmatic hypotheses (e.g., verifying SR outperforming GBN under loss, pipelining scaling with window, RTO policy speedups, and reordering resilience).

---

## 2. Archit's Viva Defense (Channel & RTO)

### Q1: How does a seed make loss and impairments repeatable?
> **Answer:**
> In userspace network emulation, each direction maintains its own dedicated pseudorandom number generator instantiated from the master seed: `random.Random(seed * 2)` for forward DATA packets and `random.Random(seed * 2 + 1)` for reverse ACK packets. Because generators are separated by direction, lost or delayed ACKs cannot consume draws from the DATA generator. Consequently, the sequence of random numbers drawn for loss, corruption, duplication, and reordering remains strictly identical across runs with the same seed, dropping exactly the same packets every time.

### Q2: Walk me through the RTO derivation for samples 40 ms, 60 ms, and 50 ms.
> **Answer:**
> Following RFC 6298 with clock granularity $G = 10\text{ ms}$:
> - **Initial state**: No samples received; default $\text{RTO} = 1.0\text{ s}$ ($1000\text{ ms}$).
> - **Sample 1 ($R = 40\text{ ms}$)**:
>   - First sample initializes estimator directly: $\text{SRTT} = 40.0\text{ ms}$, $\text{RTTVAR} = 40.0 / 2 = 20.0\text{ ms}$.
>   - $\text{RTO} = 40.0 + \max(10, 4 \times 20.0) = 40.0 + 80.0 = \mathbf{120.0\text{ ms}}$.
> - **Sample 2 ($R = 60\text{ ms}$)**:
>   - Update RTTVAR first using previous SRTT: $\text{RTTVAR} = 0.75 \times 20.0 + 0.25 \times |40.0 - 60.0| = 15.0 + 5.0 = 20.0\text{ ms}$.
>   - Update SRTT: $\text{SRTT} = 0.875 \times 40.0 + 0.125 \times 60.0 = 35.0 + 7.5 = 42.5\text{ ms}$.
>   - $\text{RTO} = 42.5 + \max(10, 4 \times 20.0) = 42.5 + 80.0 = \mathbf{122.5\text{ ms}}$.
> - **Sample 3 ($R = 50\text{ ms}$)**:
>   - Update RTTVAR: $\text{RTTVAR} = 0.75 \times 20.0 + 0.25 \times |42.5 - 50.0| = 15.0 + 0.25 \times 7.5 = 15.0 + 1.875 = 16.875\text{ ms}$.
>   - Update SRTT: $\text{SRTT} = 0.875 \times 42.5 + 0.125 \times 50.0 = 37.1875 + 6.25 = 43.4375\text{ ms}$.
>   - $\text{RTO} = 43.4375 + \max(10, 4 \times 16.875) = 43.4375 + 67.5 = 110.9375\text{ ms} \approx \mathbf{110.9\text{ ms}}$.

### Q3: Why can a normal packet never overtake the one before it, and how is reordering produced?
> **Answer:**
> A physical link enforces first-in, first-out (FIFO) transmission order. The channel loop enforces this by tracking `last_departure` time for each direction. When a normal packet arrives, its scheduled send time is bounded by $\max(\text{arrival} + \text{delay}, \text{last\_departure})$, ensuring it never leaves the channel earlier than the packet that arrived before it.
> Reordering is deliberately induced by drawing from a reorder probability: when triggered, an intentional 30 ms hold-back is appended to the packet's delay. Because its total delay now exceeds the normal threshold ($\text{delay} + \text{jitter}$), the channel exempts it from updating `last_departure`, allowing subsequent normal packets to be dispatched ahead of it.
