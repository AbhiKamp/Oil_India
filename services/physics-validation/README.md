# Physics Validation Engine

Deterministic first-principles petroleum engineering validation rules guaranteeing that machine learning outputs obey physical laws of conservation, fluid dynamics, and rock mechanics.

---

## Capabilities

- **`hydraulics.py`**:
  - Bingham Plastic annular pressure drop and laminar/turbulent velocity profile.
- **`ecd.py`**:
  - Dynamic Equivalent Circulating Density combining annular frictional loss with cuttings volumetric concentration.
- **`stuck_pipe_rules.py`**:
  - Physical differential sticking overbalance pull force and annular solids bridging criteria.
- **`kick_rules.py`**:
  - Fluid mass balance, flow delta, and pit gain rate of influx.
- **`torque_drag.py`**:
  - 3D soft-string tension, hookload, and normal contact friction back-calculation.
- **`confidence.py`**:
  - Sensor physical consistency evaluation.
