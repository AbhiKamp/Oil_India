"""
StrataSentry-NWIS: Driller Recommendation & SOP Builder
Generates actionable, standardized petroleum engineering SOPs for driller cabin display.
"""

from typing import List, Dict, Any

class DrillerRecommendationBuilder:
    @staticmethod
    def build_recommendations(hazard_type: str, severity: str, formation: str) -> List[str]:
        if hazard_type == "HOLE_PACKOFF":
            return [
                "IMMEDIATE: Stop drilling ahead and disengage auto-driller.",
                "Pick up drillstring off bottom by 2-5 meters before pack consolidates.",
                "Establish circulation at 2,400 LPM with low rotary speed (35-45 RPM) to break incipient bridges.",
                "DO NOT jar downwards if string becomes tight while picking up.",
                "Inspect shale shaker screens for splintery cavings and coal spalls.",
                "If pressure does not normalize within 5 minutes, prepare a 40-bbl high-viscosity sweep pill."
            ]
        elif hazard_type == "DIFFERENTIAL_STICKING":
            return [
                "IMMEDIATE: Attempt to rotate and reciprocate string to break filter cake bond.",
                "Reduce mud hydrostatic overbalance if formation pore pressure margins permit.",
                "Spot a 35-bbl spotting fluid / pipe-release pill (lubricant/surfactant) across permeable sands.",
                "Apply maximum allowable downward torque and jar downwards with double-acting hydraulic jars.",
                "Maintain continuous circulation through bit nozzles to avoid packing off."
            ]
        elif hazard_type == "GAS_KICK":
            return [
                "CRITICAL WELL CONTROL: Stop rotary and pick off bottom to space out tool joint.",
                "Shut down mud pumps and perform immediate positive flow check.",
                "If well is flowing, shut in well immediately using Annular Blowout Preventer (BOP).",
                "Notify Rig Superintendent / Toolpusher immediately.",
                "Record stabilized Shut-In Drillpipe Pressure (SIDPP) and Shut-In Casing Pressure (SICP).",
                "Calculate kill mud weight and initiate Wait & Weight or Driller's Method."
            ]
        elif hazard_type == "LOST_CIRCULATION":
            return [
                "Reduce mud pump rate to minimize annular dynamic friction pressure against weak formation.",
                "Monitor active pit levels and prepare LCM (Lost Circulation Material) pill with coarse CaCO3 / mica.",
                "Check ECD versus formation fracture gradient.",
                "Prepare to spot 30-bbl high-fluid-loss squeeze or thixotropic bentonite pill."
            ]
        else:
            return [
                "Parameters nominal. Continue drilling ahead observing standard tripping schedules.",
                "Maintain mud weight and viscosity per drilling program specifications."
            ]
