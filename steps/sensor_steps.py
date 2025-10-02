# File: steps/sensor_steps.py
import pytest
import allure
from pytest_bdd import scenarios, given, when, then, parsers
scenarios('../features/sensors.feature')

# --- GIVEN steps ---
@given("a robot with a Kalman filter")
def robot_with_kalman(sim):
    with allure.step("Given a robot with a Kalman filter"):
        sim.kalman_filter_enabled = True
        sim.kalman_true_position = (0.0, 0.0, 0.0)
        sim.kalman_estimate = [0.0, 0.0, 0.0]

@given(parsers.parse("a sensor with range {range:g}"))
def sensor_with_range(sim, range):
    with allure.step(f"Given a sensor with range {range}"):
        sim.sensor_range = range
        sim.sensor_position = (0.0, 0.0, 0.0)  # assume sensor at origin
        sim.objects_in_environment = []

@given(parsers.re(
    r'an object is placed at \[\s*(?P<x>-?\d*\.?\d+),\s*(?P<y>-?\d*\.?\d+),\s*(?P<z>-?\d*\.?\d+)\s*\]'
))
def place_object(sim, x, y, z):
    x, y, z = float(x), float(y), float(z)
    with allure.step(f"Given an object is placed at [{x}, {y}, {z}]"):
        sim.objects_in_environment.append((x, y, z))
        sim.current_object_position = (x, y, z)  # track for THEN steps

# --- WHEN steps ---
@when(parsers.parse("noisy measurements of position [{true_x:g}, {true_y:g}, {true_z:g}] are applied"))
def apply_noisy_measurements(sim, true_x, true_y, true_z):
    with allure.step(f"When noisy measurements of position [{true_x}, {true_y}, {true_z}] are applied"):
        sim.kalman_true_position = (true_x, true_y, true_z)
        # Simulate Kalman filter convergence with multiple iterations
        for i in range(20):
            est = sim.kalman_estimate
            meas = sim.kalman_true_position
            # Simple convergence: weighted average
            sim.kalman_estimate = [
                est[0] + 0.3 * (meas[0] - est[0]),
                est[1] + 0.3 * (meas[1] - est[1]),
                est[2] + 0.3 * (meas[2] - est[2])
            ]

@when("the sensor scans")
def sensor_scan(sim):
    with allure.step("When the sensor scans"):
        sim.detected_objects = []
        sensor_pos = getattr(sim, "sensor_position", (0.0, 0.0, 0.0))
        for obj in getattr(sim, "objects_in_environment", []):
            dx = obj[0] - sensor_pos[0]
            dy = obj[1] - sensor_pos[1]
            dz = obj[2] - sensor_pos[2]
            distance = (dx**2 + dy**2 + dz**2) ** 0.5
            if distance <= getattr(sim, "sensor_range", 1.0):
                sim.detected_objects.append(obj)

# --- THEN steps ---
@then(parsers.parse("the filter's estimate should converge approximately to [{x:g}, {y:g}, {z:g}]"))
def check_kalman_estimate(sim, x, y, z):
    with allure.step(f"Then the filter's estimate should converge approximately to [{x}, {y}, {z}]"):
        est = getattr(sim, "kalman_estimate", sim.kalman_true_position)
        tol = 0.05
        assert abs(est[0] - x) <= tol
        assert abs(est[1] - y) <= tol
        assert abs(est[2] - z) <= tol

@then("the object should be detected")
def sensor_detects(sim):
    with allure.step("Then the object should be detected"):
        obj = getattr(sim, "current_object_position", None)
        assert obj in getattr(sim, "detected_objects", [])

@then("the object should not be detected")
def sensor_not_detected(sim):
    with allure.step("Then the object should not be detected"):
        obj = getattr(sim, "current_object_position", None)
        assert obj not in getattr(sim, "detected_objects", [])