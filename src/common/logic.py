"""Small, dependency-free rules shared by the ECU applications.

Keeping these rules separate makes them easy to explain and test without
starting the SOME/IP daemon.
"""

VEHICLE_STOPPED = 0
VEHICLE_MOVING = 1
OVERSPEED_LIMIT_KMPH = 80
MIN_TARGET_TEMPERATURE_TENTHS = 160  # 16.0 degrees C
MAX_TARGET_TEMPERATURE_TENTHS = 300  # 30.0 degrees C


def vehicle_state_from_speed(speed_kmph: int) -> int:
    """Return STOPPED for zero speed, otherwise MOVING."""
    if speed_kmph < 0:
        raise ValueError("Vehicle speed cannot be negative")
    return VEHICLE_STOPPED if speed_kmph == 0 else VEHICLE_MOVING


def is_overspeed(speed_kmph: int) -> bool:
    """The warning is raised strictly above 80 km/h."""
    if speed_kmph < 0:
        raise ValueError("Vehicle speed cannot be negative")
    return speed_kmph > OVERSPEED_LIMIT_KMPH


def is_valid_target_temperature(temperature_tenths: int) -> bool:
    """Check the inclusive 16.0–30.0 C target-temperature range.

    The value is stored in tenths of a degree to avoid floating-point
    serialization (for example, 22.0 C is represented by 220).
    """
    return MIN_TARGET_TEMPERATURE_TENTHS <= temperature_tenths <= MAX_TARGET_TEMPERATURE_TENTHS
