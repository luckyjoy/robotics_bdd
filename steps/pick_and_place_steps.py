# steps/pick_and_place_steps.py
import pytest
import allure
from pytest_bdd import scenarios, given, when, then, parsers
from simulation.robot_sim import RobotSim

scenarios('../features/pick_and_place.feature')


# Fixture for the simulation
@pytest.fixture
def sim():
    return RobotSim(gui=False)

# --- GIVEN steps ---

@given(parsers.parse("a robot with a gripper at position [{x:g}, {y:g}, {z:g}]"))
def robot_with_gripper(sim, x, y, z):
    with allure.step(f"Given a robot with a gripper at position [{x}, {y}, {z}]"):
        sim.unblock_gripper()
        sim.set_position(x, y, z)
    return sim

@given(parsers.parse("a robot with a blocked gripper at position [{x:g}, {y:g}, {z:g}]"))
def robot_with_blocked_gripper(sim, x, y, z):
    with allure.step(f"Given a robot with a blocked gripper at position [{x}, {y}, {z}]"):
        sim.block_gripper()
        sim.set_position(x, y, z)
    return sim

@given(parsers.parse("an object is placed at [{x:g}, {y:g}, {z:g}]"))
def place_object(sim, x, y, z):
    with allure.step(f"Given an object is placed at [{x}, {y}, {z}]"):
        sim.place_object((x, y, z))
    return sim

# --- WHEN steps ---

@when("the robot picks up an object")
def robot_picks(sim):
    with allure.step("When the robot picks up an object"):
        sim.pick_result = sim.pick_object()

@when("the robot tries to pick up an object")
def robot_tries_pick(sim):
    with allure.step("When the robot tries to pick up an object"):
        sim.pick_result = sim.pick_object()

@when(parsers.parse("the robot moves the object to position [{x:g}, {y:g}, {z:g}]"))
def move_object(sim, x, y, z):
    with allure.step(f"When the robot moves the object to position [{x}, {y}, {z}]"):
        sim.move_result = sim.move_object_to(x, y, z)

# --- THEN steps ---

@then(parsers.parse("the object should be at position [{x:g}, {y:g}, {z:g}]"))
def check_object_position(sim, x, y, z):
    with allure.step(f"Then the object should be at position [{x}, {y}, {z}]"):
        pos = sim.object_position
        assert abs(pos[0] - x) < 1e-6
        assert abs(pos[1] - y) < 1e-6
        assert abs(pos[2] - z) < 1e-6
        assert sim.holding_object is True
        assert sim.move_result is True

@then("the pick should fail")
def check_pick_failed(sim):
    with allure.step("Then the pick should fail"):
        assert sim.pick_result is False
        assert sim.holding_object is False