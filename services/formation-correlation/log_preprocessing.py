"""
StrataSentry-NWIS: Well Log Preprocessing
Normalizes, despikes, and resamples wireline / LWD petrophysical logs (GR, RES, RHOB).
"""

from typing import List, Tuple
import numpy as np

class LogPreprocessor:
    @staticmethod
    def despike_and_normalize(values: List[float], min_val: float = 0.0, max_val: float = 200.0) -> np.ndarray:
        """
        Clamps spikes and applies Min-Max normalization (0.0 to 1.0).
        """
        arr = np.array(values, dtype=float)
        # Replace NaNs with median
        nan_mask = np.isnan(arr)
        if np.any(nan_mask):
            median_val = np.nanmedian(arr) if not np.all(nan_mask) else min_val
            arr[nan_mask] = median_val

        # Clamping
        arr = np.clip(arr, min_val, max_val)

        # Min-max scale
        denom = max_val - min_val
        if denom == 0:
            return np.zeros_like(arr)
        return (arr - min_val) / denom

    @staticmethod
    def resample_log(depths: List[float], values: List[float], step: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Uniformly resamples a log to fixed depth increments (e.g. 0.5m).
        """
        d_arr = np.array(depths)
        v_arr = np.array(values)
        if len(d_arr) < 2:
            return d_arr, v_arr

        new_depths = np.arange(d_arr.min(), d_arr.max() + step, step)
        new_values = np.interp(new_depths, d_arr, v_arr)
        return new_depths, new_values
