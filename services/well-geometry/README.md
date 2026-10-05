# Well Geometry Engine

Mathematical and geospatial calculation service implementing the petroleum industry standard **Minimum Curvature Method (MCM)** for 3D borehole directional trajectories.

---

## Capabilities

- **`minimum_curvature.py`**:
  - Implements API Bull D20 / SPE exact circular arc formulation.
  - Computes $\Delta TVD$, $\Delta Northing$, $\Delta Easting$, Ratio Factor ($F$), and Dogleg Severity ($DLS$, $^\circ/30\text{ m}$).
- **`trajectory_builder.py`**:
  - Chains consecutive survey stations into coherent 3D trajectories with closure distances.
- **`tvd_calculator.py`**:
  - Fast piecewise interpolation between survey stations.
- **`spatial_queries.py`**:
  - 3D Euclidean and ellipsoidal distance calculations for offset well proximity and collision prevention.
