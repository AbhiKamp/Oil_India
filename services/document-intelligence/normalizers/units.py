"""
StrataSentry-NWIS: Petroleum Engineering Unit Normalization
Converts between Oilfield, SI Metric, and Canadian units.
"""

class UnitNormalizer:
    # Pressure
    @staticmethod
    def psi_to_bar(psi: float) -> float:
        return psi * 0.0689476

    @staticmethod
    def bar_to_psi(bar: float) -> float:
        return bar / 0.0689476

    # Depth
    @staticmethod
    def feet_to_meters(ft: float) -> float:
        return ft * 0.3048

    @staticmethod
    def meters_to_feet(m: float) -> float:
        return m / 0.3048

    # Density / Mud Weight
    @staticmethod
    def ppg_to_sg(ppg: float) -> float:
        """Pounds per gallon to Specific Gravity"""
        return ppg * 0.119826

    @staticmethod
    def sg_to_ppg(sg: float) -> float:
        """Specific Gravity to Pounds per gallon"""
        return sg / 0.119826

    # Flow Rate
    @staticmethod
    def gpm_to_lpm(gpm: float) -> float:
        """Gallons per minute to Liters per minute"""
        return gpm * 3.78541

    @staticmethod
    def lpm_to_gpm(lpm: float) -> float:
        return lpm / 3.78541

    # Volume
    @staticmethod
    def bbl_to_m3(bbl: float) -> float:
        """Oil barrels to cubic meters"""
        return bbl * 0.158987

    @staticmethod
    def m3_to_bbl(m3: float) -> float:
        return m3 / 0.158987
