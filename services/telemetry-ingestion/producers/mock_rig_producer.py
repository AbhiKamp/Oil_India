"""
StrataSentry-NWIS: Mock Rig Telemetry Producer
Generates continuous MWD/LWD drilling streams for development, testing, and edge validation.
"""

import time
import random
from datetime import datetime
from typing import Dict, Any, Generator

class MockRigProducer:
    def __init__(self, well_id: str = "NHK-421", start_depth: float = 2845.0):
        self.well_id = well_id
        self.depth = start_depth
        self.bit_depth = start_depth - 0.2

    def generate_packets(self, rate_hz: float = 1.0, inject_packoff: bool = False) -> Generator[Dict[str, Any], None, None]:
        step = 0
        while True:
            step += 1
            if inject_packoff and step > 30:
                # Packoff divergence
                spp = 2820.0 + min(800.0, (step - 30) * 25.0) + random.uniform(-10, 10)
                torque = 14.5 + min(12.0, (step - 30) * 0.4) + random.uniform(-3, 3)
                rop = max(1.0, 14.0 - (step - 30) * 0.35)
                flow_out = max(65.0, 75.0 - (step - 30) * 0.25)
                ecd = 1.32 + min(0.12, (step - 30) * 0.003)
            else:
                spp = 2820.0 + random.uniform(-15, 15)
                torque = 14.2 + random.uniform(-0.5, 0.5)
                rop = 14.0 + random.uniform(-0.5, 0.5)
                flow_out = 75.0 + random.uniform(-0.5, 0.5)
                ecd = 1.32 + random.uniform(-0.005, 0.005)

            self.depth += (rop / 3600.0) / rate_hz
            self.bit_depth = self.depth - 0.2

            yield {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "well_id": self.well_id,
                "measured_depth": round(self.depth, 3),
                "bit_depth": round(self.bit_depth, 3),
                "rop": round(rop, 2),
                "wob": round(12.0 + random.uniform(-0.3, 0.3), 2),
                "surface_torque": round(torque, 2),
                "rotary_rpm": 110 if rop > 3 else 75,
                "standpipe_pressure": round(spp, 1),
                "flow_in": 2400.0,
                "flow_out_pct": round(flow_out, 1),
                "pit_volume": round(42.0 + random.uniform(-0.1, 0.1), 2),
                "mud_weight_in": 1.28,
                "ecd": round(ecd, 3),
                "gamma_ray": round(85.0 + random.uniform(-3, 3), 1),
                "gas_total": 18.5
            }
            time.sleep(1.0 / rate_hz)
