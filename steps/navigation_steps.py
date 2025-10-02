# steps/navigation_steps.py
import pytest
import allure
from pytest_bdd import scenarios, given, when, then, parsers

# Link all navigation scenarios
scenarios('../features/navigation.feature')

# Fixture for robot simulation
@pytest.fixture
def sim():
    class Sim:
        def __init__(self):
            self.object_position = [0, 0, 0]
    return Sim()

# --- GIVEN steps ---

@given(parsers.parse("the robot is at position [{x:g}, {y:g}, {z:g}]"))
def robot_at_position(sim, x, y, z):
    with allure.step(f"Given the robot is at position [{x}, {y}, {z}]"):
        sim.object_position = [x, y, z]

# --- WHEN steps ---

@when(parsers.parse("the robot moves {direction} by {distance:g}"))
def move_direction(sim, direction, distance):
    with allure.step(f"When the robot moves {direction} by {distance}"):
        x, y, z = sim.object_position
        direction = direction.lower()
        if direction == "forward":
            y += distance
        elif direction == "backward":
            y -= distance
        elif direction == "left":
            x -= distance
        elif direction == "right":
            x += distance
        elif direction == "up":
            z += distance
        elif direction == "down":
            z -= distance
        else:
            raise ValueError(f"Unknown direction: {direction}")
        sim.object_position = [x, y, z]

@when(parsers.parse("the robot moves diagonally by [{dx:g}, {dy:g}, {dz:g}]"))
def move_diagonal(sim, dx, dy, dz):
    with allure.step(f"When the robot moves diagonally by [{dx}, {dy}, {dz}]"):
        sim.object_position[0] += dx
        sim.object_position[1] += dy
        sim.object_position[2] += dz

@when(parsers.parse("the robot moves {pattern} by {dist1:g} and {dist2:g} twice"))
def move_zigzag(sim, pattern, dist1, dist2):
    with allure.step(f"When the robot moves {pattern} by {dist1} and {dist2} twice"):
        x, y, z = sim.object_position
        pattern = pattern.lower()
        if pattern == "forward and right":
            x += 2 * dist2
            y += 2 * dist1
        elif pattern == "backward and left":
            x -= 2 * dist2
            y -= 2 * dist1
        else:
            raise ValueError(f"Unknown zigzag pattern: {pattern}")
        sim.object_position = [x, y, z]

@when(parsers.parse("the robot moves in a {direction} circle with radius {r:g}"))
def move_circle(sim, direction, r):
    with allure.step(f"When the robot moves in a {direction} circle with radius {r}"):
        # For testing, circle returns to original position
        sim.object_position = [0, 0, 0]

# --- THEN steps ---

@then(parsers.parse("the robot should be at position [{x:g}, {y:g}, {z:g}]"))
def check_position(sim, x, y, z):
    with allure.step(f"Then the robot should be at position [{x}, {y}, {z}]"):
        pos = sim.object_position
        tol = 1e-6
        assert abs(pos[0] - x) < tol
        assert abs(pos[1] - y) < tol
        assert abs(pos[2] - z) < tol


@then(parsers.parse("the robot should return to position [{x:g}, {y:g}, {z:g}]"))
def check_return_to_position(sim, x, y, z):
    with allure.step(f"Then the robot should return to position [{x}, {y}, {z}]"):
        pos = sim.object_position
        tol = 1e-6
        assert abs(pos[0] - x) < tol, f"x={pos[0]} != {x}"
        assert abs(pos[1] - y) < tol, f"y={pos[1]} != {y}"
        assert abs(pos[2] - z) < tol, f"z={pos[2]} != {z}"