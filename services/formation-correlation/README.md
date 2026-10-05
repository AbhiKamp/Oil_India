# Formation Correlation Engine

Sub-surface geological alignment and boundary prediction service matching real-time MWD logs against offset reference wells using **Dynamic Time Warping (DTW)**.

---

## Capabilities

- **`log_preprocessing.py`**: Despiking, null-filling, and depth resampling.
- **`dtw_alignment.py`**: Constrained Dynamic Time Warping with Sakoe-Chiba band to prevent unrealistic geological warping.
- **`gamma_ray_alignment.py`**: Stratigraphic curve correlation against offset Gamma Ray logs.
- **`resistivity_alignment.py`**: Logarithmic deep resistivity alignment.
- **`formation_matcher.py`**: Projects structural formation entry depths ahead of the active drill bit.
