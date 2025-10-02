# File: features/safety.feature
@safety
Feature: Robot safety
  Ensure that the robot operates within safe limits and avoids collisions.

  @safety @boundary_check
  Scenario Outline: <REQ_SAF_01> Robot does not cross boundary from various positions
    Given a robot at position [<start_x>, <start_y>, <start_z>]
    When the robot attempts to move to [<target_x>, <target_y>, <target_z>]
    Then the robot should remain within boundaries

    Examples:
      | start_x | start_y | start_z | target_x | target_y | target_z |
      | 0       | 0       | 0       | 2        | 0        | 0        |
      | 1       | 1       | 1       | 3        | -1       | 2        |
      | 0.5     | 0.5     | 0.5     | -1       | 2        | 1        |
      | 2       | 2       | 0       | 4        | 0        | 0        |
      | 0       | 1       | 2       | -2       | 3        | 1        |
      | 0       | 0       | 0       | 10       | 10       | 10       |  # far out-of-bounds
      | 5       | 5       | 0       | 5        | 5        | 5        |   # move within bounds

  @safety @arm_collision
  Scenario Outline: <REQ_SAF_02> Robot arm avoids single obstacle
    Given a robot at position [<start_x>, <start_y>, <start_z>]
    And an obstacle is at [<obs_x>, <obs_y>, <obs_z>]
    When the robot moves its arm to [<target_x>, <target_y>, <target_z>]
    Then the robot arm should stop before the obstacle

    Examples:
      | start_x | start_y | start_z | obs_x | obs_y | obs_z | target_x | target_y | target_z |
      | 0       | 0       | 0       | 0.5   | 0     | 0     | 1        | 0        | 0        |
      | 1       | 1       | 1       | 1.5   | 1     | 1     | 2        | 1        | 1        |
      | 0       | 0       | 0       | 0     | 0.5   | 0     | 0        | 1        | 0        |
      | 2       | 0       | 0       | 2     | 0.5   | 0     | 2        | 1        | 0        |
      | 1       | 1       | 0       | 1     | 1     | 0.5   | 1        | 1        | 1        |
      | 0       | 0       | 0       | 0.5   | 0.5   | 0.5   | 1        | 1        | 1        |  # diagonal collision
      | 0       | 0       | 0       | 0     | 0     | 0.5   | 0        | 0        | 1        |  # vertical collision

  @safety @multiple_obstacles
  Scenario Outline: <REQ_SAF_03> Robot arm avoids multiple obstacles
    Given a robot at position [<start_x>, <start_y>, <start_z>]
    And obstacles are at [<obs1_x>, <obs1_y>, <obs1_z>] and [<obs2_x>, <obs2_y>, <obs2_z>]
    When the robot moves its arm to [<target_x>, <target_y>, <target_z>]
    Then the robot arm should stop before the nearest obstacle

    Examples:
      | start_x | start_y | start_z | obs1_x  | obs1_y  | obs1_z | obs2_x | obs2_y | obs2_z | target_x | target_y | target_z |
      | 0       | 0       | 0       |  0.5    |  0      | 0      |  1     | 0      | 0      | 2        | 0        | 0        |
      | 0       | 0       | 0       |  0      |  0.5    | 0      |  0     | 1      | 0      | 0        | 2        | 0        |
      | 1       | 1       | 1       |  1.5    |  1      | 1      |  2     | 1      | 1      | 3        | 1        | 1        |
