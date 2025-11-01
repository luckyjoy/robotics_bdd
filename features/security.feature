@all @security
Feature: Robotics Security and Access Control

  As a security engineer,
  I want to verify that unauthorized users cannot execute critical commands,
  So that the robot and its environment remain secure against malicious actions.

  @security @access_control
  Scenario Outline: Unauthorized user attempts to execute a restricted command

    Given the simulated robot is connected and operational
    And the user logs in with the role of "<Role>"
    When the user attempts to send the critical command "<Command>"
    Then the system should return a "<Expected_Result>" status
    And the robot's state should remain "<Robot_State>"

    Examples: Access Control Matrix
      | Role           | Command                  | Expected_Result | Robot_State | Description                                         |
      | Guest          | MOVE_ARM_JOINT(5)        | Access Denied   | Unchanged   | Guest cannot move physical components.              |
      | Guest          | SYSTEM_SHUTDOWN          | Access Denied   | Operational | Guest cannot shut down the system.                  |
      | Observer       | SYSTEM_REBOOT            | Access Denied   | Operational | Observer can view, but not reboot.                  |
      | Observer       | GET_TELEMETRY_DATA       | Success         | Operational | Observer is authorized for read-only actions.       |
      | Operator       | EMERGENCY_STOP           | Success         | Stopped     | Operator must be able to halt the robot immediately.|
      | Operator       | CLEAR_ERROR_LOGS         | Success         | Operational | Operator can clear non-critical logs.               |
      | Unauthenticated| GET_SYSTEM_INFO          | Authentication Required | Operational | No information should be available without login. |
      | Administrator  | UPDATE_FIRMWARE(v2.1)    | Success         | Operational | Admin authorized for system updates.                |


  @security @input_validation
  Scenario: Command injection vulnerability check

    Given the simulated robot is connected and awaiting commands
    When an unauthenticated user attempts to send a command with a shell injection payload
      """
      MOVE_ARM_JOINT(10); rm -rf /
      """
    Then the system should strictly reject the command due to invalid characters
    And the robot should not execute any part of the payload
    And the system should log an attempt at "Command Injection"
