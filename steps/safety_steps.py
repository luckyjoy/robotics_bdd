# steps/safety_steps.py
import pytest
import math
import allure
from pytest_bdd import scenarios, given, when, then, parsers
scenarios('../features/safety.feature')

# --- GIVEN steps ---
@given(parsers.parse("a robot at position [{x:g}, {y:g}, {z:g}]"))
def robot_at_position(sim, x, y, z):
    with allure.step(f"Given a robot at position [{x}, {y}, {z}]"):
        sim.object_position = [x, y, z]

@given(parsers.parse("an obstacle is at [{x:g}, {y:g}, {z:g}]"))
def obstacle_at(sim, x, y, z):
    with allure.step(f"Given an obstacle is at [{x}, {y}, {z}]"):
        if not hasattr(sim, 'obstacles'):
            sim.obstacles = []
        sim.obstacles.append((x, y, z))

@given(parsers.parse("obstacles are at [{x1:g}, {y1:g}, {z1:g}] and [{x2:g}, {y2:g}, {z2:g}]"))
def multiple_obstacles(sim, x1, y1, z1, x2, y2, z2):
    with allure.step(f"Given obstacles are at [{x1}, {y1}, {z1}] and [{x2}, {y2}, {z2}]"):
        sim.obstacles = [(x1, y1, z1), (x2, y2, z2)]

# --- WHEN steps ---
@when(parsers.parse("the robot attempts to move to [{x:g}, {y:g}, {z:g}]"))
def robot_attempt_move(sim, x, y, z):
    with allure.step(f"When the robot attempts to move to [{x}, {y}, {z}]"):
        min_bound, max_bound = getattr(sim, 'boundary', ((0,0,0), (1,1,1)))
        new_pos = (
            max(min(x, max_bound[0]), min_bound[0]),
            max(min(y, max_bound[1]), min_bound[1]),
            max(min(z, max_bound[2]), min_bound[2]),
        )
        sim.object_position = list(new_pos)

@when(parsers.parse("the robot moves its arm to [{x:g}, {y:g}, {z:g}]"))
def robot_move_arm(sim, x, y, z):
    with allure.step(f"When the robot moves its arm to [{x}, {y}, {z}]"):
        if not hasattr(sim, 'arm_position'):
            sim.arm_position = list(sim.object_position)

        target = [x, y, z]
        step_count = 50
        for i in range(1, step_count + 1):
            intermediate = [
                sim.arm_position[j] + (target[j] - sim.arm_position[j]) * i / step_count
                for j in range(3)
            ]
            collision = False
            for obs in getattr(sim, 'obstacles', []):
                # check if arm is within 0.1 units in all axes (3D proximity)
                if all(abs(intermediate[j] - obs[j]) < 0.1 for j in range(3)):
                    collision = True
                    break
            if collision:
                break
            sim.arm_position = intermediate

# --- THEN steps ---
@then("the robot should remain within boundaries")
def check_boundary(sim):
    with allure.step("Then the robot should remain within boundaries"):
        min_bound, max_bound = getattr(sim, 'boundary', ((0,0,0), (1,1,1)))
        x, y, z = sim.object_position
        assert min_bound[0] <= x <= max_bound[0]
        assert min_bound[1] <= y <= max_bound[1]
        assert min_bound[2] <= z <= max_bound[2]

@then("the robot arm should stop before the obstacle")
def check_arm_collision(sim):
    with allure.step("Then the robot arm should stop before the obstacle"):
        arm_pos = getattr(sim, 'arm_position', sim.object_position)
        for obs in getattr(sim, 'obstacles', []):
            dist = math.sqrt(sum((a - o)**2 for a, o in zip(arm_pos, obs)))
            assert dist >= 0.1, f"Arm at {arm_pos} overlaps obstacle at {obs}"

@then("the robot arm should stop before the nearest obstacle")
def check_arm_collision_nearest(sim):
    with allure.step("Then the robot arm should stop before the nearest obstacle"):
        arm_pos = getattr(sim, 'arm_position', sim.object_position)
        min_dist = min(
            math.sqrt(sum((a - o)**2 for a, o in zip(arm_pos, obs)))
            for obs in getattr(sim, 'obstacles', [])
        )
        assert min_dist >= 0.1, f"Arm at {arm_pos} overlaps nearest obstacle"