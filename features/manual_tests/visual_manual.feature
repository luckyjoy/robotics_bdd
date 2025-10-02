#File: features/manual/visual_manual.feature
@manual 
Feature: Navigation Visual and Locomotion Fidelity
Verifies the visual smoothness and positional accuracy of complex movements,
translating manual observation into measurable acceptance criteria.

Scenario: <REQ_NAV_05> Circular path execution is smooth and returns to origin
Given the robot is initialized at position [0, 0, 0]
And the required path is a circle with radius 1.5 meters
When the robot executes the full circular path
Then the robot's final position should be within 0.05 units of the origin [0, 0, 0]
And the system should confirm the path tracking error (PTE) was below 0.1 units during the execution

@MT_NAV_002 
Scenario: <REQ_NAV_04> Complex zigzag movement follows trajectory precisely
Given the robot is initialized at position [0, 0, 0]
When the robot moves Forward by 2 units
And the robot moves Right by 1 unit
And the robot moves Forward by 2 units
And the robot moves Right by 1 unit
Then the robot should be at final position [2, 4, 0] with a tolerance of 0.05 units
And the robot's path logging confirms exactly two distinct 90-degree pivots were executed

@MT_WALK_003 
Scenario Outline: Robot's chest successfully touches ground after crouch
Given a robot is at position [<start_x>, <start_y>, <start_z>] on a surface
When the robot executes the crouch maneuver
Then the robot's chest (contact point Z) should be less than 0.01 units from the ground plane
And the system state should confirm the robot is in "crouched" posture

Examples:
  | start_x | start_y | start_z |
  | 0       | 0       | 0       |
  | 1       | 1       | 0.5     |
