"""
alerting.py

Applies specification/threshold checks to incoming sensor readings,
flagging out-of-tolerance (OOT) conditions -- the same logic pattern
used in calibration/instrumentation deviation checking.
"""

from dataclasses import dataclass
from data_source import SensorReading

# Reference specification limits (would come from an instrument's
# calibration/spec sheet in a real deployment)
LIMITS = {
    "temperature_c": (55.0, 80.0),
    "pressure_bar": (3.5, 5.5),
    "flow_lpm": (90.0, 150.0),
    "vibration_mm_s": (0.0, 3.5),
}


@dataclass
class Deviation:
    parameter: str
    value: float
    low: float
    high: float


def check_deviations(reading: SensorReading) -> list[Deviation]:
    """Return a list of parameters that are out of tolerance."""
    deviations = []
    values = {
        "temperature_c": reading.temperature_c,
        "pressure_bar": reading.pressure_bar,
        "flow_lpm": reading.flow_lpm,
        "vibration_mm_s": reading.vibration_mm_s,
    }
    for param, value in values.items():
        low, high = LIMITS[param]
        if value < low or value > high:
            deviations.append(Deviation(param, value, low, high))
    return deviations


def severity(deviations: list[Deviation]) -> str:
    """Simple severity classification based on number of deviating parameters."""
    if not deviations:
        return "Normal"
    if len(deviations) == 1:
        return "Warning"
    return "Critical"
