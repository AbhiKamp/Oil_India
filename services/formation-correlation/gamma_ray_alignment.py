"""
StrataSentry-NWIS: Gamma Ray Log Alignment
Cross-correlates MWD Gamma Ray curves to match lithological marker beds against offset wells.
"""

from typing import List, Dict, Any
import numpy as np
try:
    from .log_preprocessing import LogPreprocessor
    from .dtw_alignment import DynamicTimeWarpingAligner
except ImportError:
    from log_preprocessing import LogPreprocessor
    from dtw_alignment import DynamicTimeWarpingAligner

class GammaRayAligner:
    def __init__(self):
        self.preprocessor = LogPreprocessor()
        self.dtw = DynamicTimeWarpingAligner()

    def correlate_logs(
        self,
        active_depths: List[float],
        active_gr: List[float],
        offset_depths: List[float],
        offset_gr: List[float]
    ) -> Dict[str, Any]:
        """
        Calculates depth shift and DTW alignment between active and offset GR curves.
        """
        norm_active = self.preprocessor.despike_and_normalize(active_gr, 0.0, 150.0)
        norm_offset = self.preprocessor.despike_and_normalize(offset_gr, 0.0, 150.0)

        dtw_result = self.dtw.align(norm_active, norm_offset)

        # Estimate average depth shift
        shifts = []
        for a_idx, o_idx in dtw_result["path"]:
            shifts.append(offset_depths[o_idx] - active_depths[a_idx])

        mean_shift = float(np.mean(shifts)) if shifts else 0.0

        return {
            "dtw_similarity": dtw_result["similarity_score"],
            "mean_depth_shift_m": round(mean_shift, 2),
            "alignment_path_points": len(dtw_result["path"])
        }
