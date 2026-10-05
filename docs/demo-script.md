# StrataSentry-NWIS Live Demonstration Script
## Step-by-Step Operator & Evaluator Walkthrough

---

## 1. Scenario Context: Naharkatiya Well NHK-421

- **Location**: Naharkatiya Oilfield, Upper Assam Basin
- **Target Formation**: Barail Coal-Shale Sequence ($2,800\text{ m} - 3,200\text{ m}$ MD)
- **Current Operational Phase**: 8-1/2" hole section drilling ahead with PDC bit and motor BHA
- **Injected Hazard**: Simulated annular pack-off caused by coal caving at $2,845\text{ m}$ MD

---

## 2. Demonstration Step-by-Step Execution

### Step 1: Environment Initialization
```bash
# Terminal 1: Launch Backend API
uvicorn apps.api.app.main:app --port 8000 --reload

# Terminal 2: Launch Frontend Tactical HUD
cd apps/dashboard && npm run dev
```
Navigate browser to `http://localhost:3000`. Observe:
- 3D borehole trajectory viewer loading active well *NHK-421* and offset trajectories (*NHK-412*, *MOR-118*, *BGH-07*).
- Horizon surfaces for *Tipam Sandstone*, *Girujan Clay*, and *Barail Coal-Shale*.

### Step 2: Normal Drilling Baseline Replay
```bash
# Terminal 3: Start normal baseline drilling stream
python scripts/simulate_telemetry.py --well NHK-421 --rate-hz 2 --mode normal
```
- Observe real-time digital gauges and scrolling log strip charts:
  - ROP steady at $15\text{ m/hr}$
  - WOB steady at $12\text{ tons}$
  - Torque constant at $14\text{ kNm}$
  - SPP steady at $2,850\text{ psi}$
  - Risk Status: **NORMAL** (Green HUD badge)

### Step 3: Trigger Hazard Scenario (Hole Pack-Off)
```bash
# Terminal 3: Inject hole pack-off anomaly at 2,845m MD
python scripts/simulate_telemetry.py --well NHK-421 --rate-hz 2 --inject-incident packoff
```
1. **Divergence (T + 10s)**:
   - SPP begins climbing ($2,850 \rightarrow 3,200 \rightarrow 3,450\text{ psi}$).
   - Flow-out percentage exhibits small fluctuations.
   - Torque exhibits high standard deviation with micro-spalls.
2. **First Early Warning (T + 25s)**:
   - Status switches to **WATCH** (Yellow badge).
   - LSTM Autoencoder reconstruction loss spikes past the 99th percentile.
3. **Escalation to High Risk (T + 45s)**:
   - Status elevates to **WARNING** (Orange flashing HUD).
   - XGBoost pack-off probability registers $82\%$.
   - Physics engine confirms annular cuttings volume $C_v > 0.08$.
   - Driller recommendation banner pops up:
     > *"Stop drilling ahead immediately. Pick up off bottom to 2,835m MD. Circulate at 2,400 LPM with low rotary speed (40 RPM)."*

### Step 4: Explore Grounded Historical Evidence
- Click on the **Historical Evidence Drawer** on the right side of the screen.
- Notice the retrieved offset well report for **MOR-118**:
  - Exact depth: $2,848\text{ m}$ MD in Barail Coal.
  - Excerpt describing the exact same pack-off signature and how a high-viscosity pill freed the string.
  - Page reference to WCR MOR-118 Section 4.

### Step 5: Interactive AI Copilot Query
- Open the **Drilling Copilot** chat modal.
- Type: *"What is the recommended mud weight and wiper trip procedure for Barail coal at this depth?"*
- Observe grounded response with exact citations to Assam Basin offset wells.
