"""Offline tests for DriveLink application rules (no daemon required)."""
import unittest
from src.common.logic import VEHICLE_MOVING, VEHICLE_STOPPED, is_overspeed, is_valid_target_temperature, vehicle_state_from_speed

class VehicleRuleTests(unittest.TestCase):
    def test_zero_speed_is_stopped(self): self.assertEqual(vehicle_state_from_speed(0), VEHICLE_STOPPED)
    def test_positive_speed_is_moving(self):
        self.assertEqual(vehicle_state_from_speed(1), VEHICLE_MOVING)
        self.assertEqual(vehicle_state_from_speed(65), VEHICLE_MOVING)
    def test_negative_speed_is_rejected(self):
        with self.assertRaises(ValueError): vehicle_state_from_speed(-1)
    def test_overspeed_limit_is_strictly_above_80(self):
        self.assertFalse(is_overspeed(80)); self.assertTrue(is_overspeed(81)); self.assertTrue(is_overspeed(120))
    def test_negative_speed_cannot_be_overspeed(self):
        with self.assertRaises(ValueError): is_overspeed(-5)

class ClimateRuleTests(unittest.TestCase):
    def test_lower_and_upper_temperature_boundaries_are_valid(self):
        self.assertTrue(is_valid_target_temperature(160)); self.assertTrue(is_valid_target_temperature(300))
    def test_temperature_inside_range_is_valid(self):
        self.assertTrue(is_valid_target_temperature(220)); self.assertTrue(is_valid_target_temperature(245))
    def test_temperature_outside_range_is_invalid(self):
        self.assertFalse(is_valid_target_temperature(159)); self.assertFalse(is_valid_target_temperature(301)); self.assertFalse(is_valid_target_temperature(100)); self.assertFalse(is_valid_target_temperature(350))

if __name__ == "__main__": unittest.main(verbosity=2)
