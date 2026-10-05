"""
StrataSentry-NWIS: Dynamic Time Warping (DTW) Alignment
Aligns active drilling logs with offset well logs under geological monotonicity constraints.
"""

import numpy as np
from typing import Tuple, List, Dict, Any

class DynamicTimeWarpingAligner:
    def __init__(self, window_size: int = 25):
        self.window_size = window_size

    def align(self, seq_active: np.ndarray, seq_offset: np.ndarray) -> Dict[str, Any]:
        """
        Calculates constrained DTW cost matrix and optimal warping path.
        """
        n = len(seq_active)
        m = len(seq_offset)
        if n == 0 or m == 0:
            return {"distance": 0.0, "path": []}

        # Initialize cost matrix with infinity
        dtw_matrix = np.full((n + 1, m + 1), np.inf)
        dtw_matrix[0, 0] = 0.0

        w = max(self.window_size, abs(n - m))

        for i in range(1, n + 1):
            low = max(1, i - w)
            high = min(m + 1, i + w + 1)
            for j in range(low, high):
                cost = (seq_active[i - 1] - seq_offset[j - 1]) ** 2
                dtw_matrix[i, j] = cost + min(
                    dtw_matrix[i - 1, j],      # Insertion
                    dtw_matrix[i, j - 1],      # Deletion
                    dtw_matrix[i - 1, j - 1]   # Match
                )

        # Backtrack optimal warping path
        i, j = n, m
        path = []
        while i > 0 and j > 0:
            path.append((i - 1, j - 1))
            steps = [
                (dtw_matrix[i - 1, j - 1], (i - 1, j - 1)),
                (dtw_matrix[i - 1, j], (i - 1, j)),
                (dtw_matrix[i, j - 1], (i, j - 1))
            ]
            steps.sort(key=lambda x: x[0])
            next_step = steps[0][1]
            i, j = next_step

        path.reverse()
        normalized_distance = float(dtw_matrix[n, m] / (n + m))

        return {
            "distance": round(normalized_distance, 4),
            "similarity_score": round(max(0.0, 1.0 - normalized_distance * 2.0), 3),
            "path": path
        }
