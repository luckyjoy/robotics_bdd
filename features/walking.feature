# File: features/walking.feature
@walking
Feature: Robot Walking
  Verify walking and crouching behaviors

  @stand
  Scenario Outline: <REQ_WAL_01> Robot starts walking from different positions
    Given a robot at position [<start_x>, <start_y>, <start_z>]
    When the robot starts walking
    Then the robot should be walking

    Examples:
      | start_x | start_y | start_z |
      | 0       | 0       | 0       |
      | 1       | 0       | 0       |
      | 0       | 1       | 0       |
      | 1       | 1       | 1       |
	  
  @ground
  Scenario Outline: <REQ_WAL_02> Robot crouches from different positions
    Given a robot at position [<start_x>, <start_y>, <start_z>]
    When the robot crouches so that its chest touches the ground
    Then the robot should be in crouched position

    Examples:
      | start_x | start_y | start_z |
      | 0       | 0       | 0       |
      | 0       | 0       | 1       |
      | 1       | 1       | 1       |

  @walking
  Scenario Outline: <REQ_WAL_03> Robot walks forward by variable distances
    Given a robot at position [<start_x>, <start_y>, <start_z>]
    When the robot walks forward by <distance> units
    Then the robot should be at position [<end_x>, <end_y>, <end_z>]

    Examples:
      | start_x | start_y | start_z | distance | end_x | end_y | end_z |
      |   0     |   0     |   0     |  1       |  0    |  1    |  0    |
      |   0     |   1     |   0     |  2       |  0    |  3    |  0    |
      |   1     |   0     |   0     |  3       |  1    |  3    |  0    |
      |   2     |   2     |   0     |  1       |  2    |  3    |  0    |
      |  24     |  29     |  50     | 51       | 20    | 13    | 10    |