"""
StrataSentry-NWIS: Deep Resistivity Alignment
Aligns deep induction / resistivity curves to isolate hydrocarbon bearing sands vs coals.
"""

from typing import List, Dict, Any
import numpy as np
try:
    from .log_preprocessing import LogPreprocessor
    from .dtw_alignment import DynamicTimeWarpingAligner
except ImportError:
    from log_preprocessing import LogPreprocessor
    from dtw_alignment import DynamicTimeWarpingAligner

class ResistivityAligner:
    def __init__(self):
        self.preprocessor = LogPreprocessor()
        self.dtw = DynamicTimeWarpingAligner()

    def correlate_resistivity(
        self,
        active_res: List[float],
        offset_res: List[float]
    ) -> Dict[str, Any]:
        """
        Applies logarithmic scaling before normalisation and DTW.
        """
        log_act = [float(np.log10(max(0.1, r))) for r in active_res]
        log_off = [float(np.log10(max(0.1, r))) for r in offset_res]

        norm_act = self.preprocessor.despike_and_normalize(log_act, -1.0, 3.0)
        norm_off = self.preprocessor.despike_and_normalize(log_off, -1.0, 3.0)

        dtw_res = self.dtw.align(norm_act, norm_off)
        return {
            "resistivity_similarity": dtw_res["similarity_score"],
            "dtw_distance": dtw_res["distance"]
        }
