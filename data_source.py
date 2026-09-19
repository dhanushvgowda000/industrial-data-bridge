"""
data_source.py

Simulates live industrial sensor data as if read from a Modbus TCP device
(e.g., a PLC or field instrument). Each function mimics a register read.

To connect this to a REAL PLC/Modbus device instead of the simulator,
replace the body of `read_registers()` with a pymodbus client call, e.g.:

    from pymodbus.client import ModbusTcpClient
    client = ModbusTcpClient('192.168.1.10', port=502)
    result = client.read_holding_registers(address=0, count=4, slave=1)
    values = result.registers

Everything downstream (dashboard, alerting, logging) works unchanged
once real register values are plugged in here.
"""

import random
import time
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SensorReading:
    timestamp: datetime
    temperature_c: float
    pressure_bar: float
    flow_lpm: float
    vibration_mm_s: float
    fault: bool = False


class IndustrialDataSimulator:
    """
    Simulates a set of industrial sensors on a process line.
    Occasionally injects a fault/anomaly to demonstrate alerting logic,
    the same way a real deviation or OOT condition would appear.
    """

    def __init__(self, fault_probability: float = 0.04):
        self.fault_probability = fault_probability
        self._base_temp = 65.0
        self._base_pressure = 4.2
        self._base_flow = 120.0
        self._base_vibration = 1.8

    def read(self) -> SensorReading:
        fault = random.random() < self.fault_probability

        if fault:
            # Simulate an out-of-tolerance / anomalous reading
            temp = self._base_temp + random.uniform(15, 30)
            pressure = self._base_pressure + random.uniform(1.5, 3.0)
            flow = self._base_flow - random.uniform(40, 70)
            vibration = self._base_vibration + random.uniform(3, 6)
        else:
            temp = self._base_temp + random.uniform(-2, 2)
            pressure = self._base_pressure + random.uniform(-0.3, 0.3)
            flow = self._base_flow + random.uniform(-8, 8)
            vibration = self._base_vibration + random.uniform(-0.4, 0.4)

        return SensorReading(
            timestamp=datetime.now(),
            temperature_c=round(temp, 2),
            pressure_bar=round(pressure, 2),
            flow_lpm=round(flow, 2),
            vibration_mm_s=round(vibration, 2),
            fault=fault,
        )
