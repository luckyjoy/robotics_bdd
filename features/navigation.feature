# File: features/navigation.feature
@navigation
Feature: Robot Navigation
  Test various movements of the robot in 3D space

  @move
  Scenario Outline: Robot moves in a single direction
    Given the robot is at position [<start_x>, <start_y>, <start_z>]
    When the robot moves <direction> by <distance>
    Then the robot should be at position [<end_x>, <end_y>, <end_z>]

    Examples:
      | start_x | start_y | start_z | direction | distance | end_x | end_y | end_z |
      | 0       | 0       | 0       | forward   | 1        | 0     | 1     | 0     |
      | 0       | 1       | 0       | backward  | 1        | 0     | 0     | 0     |
      | 1       | 0       | 0       | left      | 1        | 0     | 0     | 0     |
      | 0       | 0       | 0       | right     | 1        | 1     | 0     | 0     |
      | 0       | 0       | 0       | up        | 1        | 0     | 0     | 1     |
      | 0       | 0       | 1       | down      | 1        | 0     | 0     | 0     |

  @diagonal
  Scenario Outline: Robot moves diagonally in 3D space
    Given the robot is at position [<start_x>, <start_y>, <start_z>]
    When the robot moves diagonally by [<dx>, <dy>, <dz>]
    Then the robot should be at position [<end_x>, <end_y>, <end_z>]

    Examples:
      | start_x | start_y | start_z | dx | dy | dz | end_x | end_y | end_z |
      | 0       | 0       | 0       | 1  | 1  | 0  | 1     | 1     | 0     |
      | 1       | 1       | 0       | -1 | -1 | 0  | 0     | 0     | 0     |
      | 0       | 0       | 0       | 0  | 1  | 1  | 0     | 1     | 1     |
      | 0       | 1       | 1       | 0  | -1 | -1 | 0     | 0     | 0     |
      | 0       | 0       | 0       | 1  | 0  | 1  | 1     | 0     | 1     |
      | 1       | 0       | 1       | -1 | 0  | -1 | 0     | 0     | 0     |
      | 1       | 0       | 0       | -1 | 0  | 1  | 0     | 0     | 1     |
      | 0       | 0       | 1       | 1  | 0  | -1 | 1     | 0     | 0     |

  @forward_backward
  Scenario Outline: Robot moves forward/backward multiple steps
    Given the robot is at position [<start_x>, <start_y>, <start_z>]
    When the robot moves <direction> by <distance>
    Then the robot should be at position [<end_x>, <end_y>, <end_z>]

    Examples:
      | start_x | start_y | start_z | direction | distance | end_x | end_y | end_z |
      | 0       | 0       | 0       | forward   | 2        | 0     | 2     | 0     |
      | 0       | 2       | 0       | backward  | 2        | 0     | 0     | 0     |
      | 0       | 0       | 0       | up        | 2        | 0     | 0     | 2     |
      | 0       | 0       | 2       | down      | 2        | 0     | 0     | 0     |

  @zigzag
  Scenario Outline: Robot zigzags forward and backward
    Given the robot is at position [<start_x>, <start_y>, <start_z>]
    When the robot moves <pattern> by <dist1> and <dist2> twice
    Then the robot should be at position [<end_x>, <end_y>, <end_z>]

    Examples:
      | start_x | start_y | start_z | pattern            | dist1 | dist2 | end_x | end_y | end_z |
      | 0       | 0       | 0       | forward and right  | 1     | 1     | 2     | 2     | 0     |
      | 2       | 2       | 0       | backward and left  | 1     | 1     | 0     | 0     | 0     |

  @circle
  Scenario Outline: Robot moves in a circle and returns to origin
    Given the robot is at position [0, 0, 0]
    When the robot moves in a <direction> circle with radius 1
    Then the robot should return to position [0, 0, 0]

    Examples:
      | direction         |
      | clockwise         |
      | counter-clockwise |
