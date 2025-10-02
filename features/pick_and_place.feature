# Filename: features/pick_and_place.feature
@pick_and_place
Feature: Pick and Place
  Test robot picking and moving objects

  @pick
  Scenario Outline: <REQ_PAP_01> Robot picks an object and moves it to different positions
    Given a robot with a gripper at position [<start_x>, <start_y>, <start_z>]
    When the robot picks up an object
    And the robot moves the object to position [<end_x>, <end_y>, <end_z>]
    Then the object should be at position [<end_x>, <end_y>, <end_z>]

    Examples:
      | start_x | start_y | start_z | end_x | end_y | end_z |
      | 0       | 0       | 0       | 1     | 1     | 0     |
      | 0       | 0       | 0       | 2     | 0     | 1     |
      | 1       | 1       | 0       | 3     | 0     | 1     |
      | 0       | 2       | 1       | 0     | 0     | 0     |
      | 2       | 0       | 0       | 1     | 1     | 1     |
      | 0       | 0       | 2       | 0     | 2     | 2     |

  @blocked
  Scenario Outline:  <REQ_PAP_02> <REQ_PAP_04> Robot cannot pick object with blocked gripper at different positions
    Given a robot with a blocked gripper at position [<start_x>, <start_y>, <start_z>]
    When the robot tries to pick up an object
    Then the pick should fail

    Examples:
      | start_x | start_y | start_z |
      | 0       | 0       | 0       |
      | 1       | 1       | 1       |
      | 2       | 0       | 1       |
      | 0       | 2       | 0       |
      | 3       | 1       | 2       |
      | 0       | 2       | 0       |

  @pick_multiple
  Scenario Outline: <REQ_PAP_03> Robot picks and moves object to various positions
    Given a robot with a gripper at position [<start_x>, <start_y>, <start_z>]
    When the robot picks up an object
    And the robot moves the object to position [<end_x>, <end_y>, <end_z>]
    Then the object should be at position [<end_x>, <end_y>, <end_z>]

    Examples:
      | start_x | start_y | start_z | end_x | end_y | end_z |
      | 0       | 0       | 0       | 2     | 2     | 0     |
      | 1       | 1       | 0       | 3     | 0     | 1     |
      | 0       | 2       | 1       | 0     | 0     | 0     |
      | 2       | 0       | 0       | 1     | 1     | 1     |
      | 0       | 0       | 2       | 0     | 2     | 2     |

