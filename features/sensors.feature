# File: features/sensors.feature
@sensors
Feature: Sensor and Filtering
  Test robot sensors and data filtering

  @kalman_filter
  Scenario Outline: Kalman filter converges to an accurate estimate
    Given a robot with a Kalman filter
    When noisy measurements of position [<true_x>, <true_y>, <true_z>] are applied
    Then the filter's estimate should converge approximately to [<true_x>, <true_y>, <true_z>]

    Examples:
      | true_x | true_y | true_z |
      | 1.0    | 0      | 0      |
      | 0      | 1.0    | 0      |
      | 0      | 0      | 1.0    |
      | 1.0    | 1.0    | 1.0    |

  @object_detection
  Scenario Outline: Sensor detects objects at various positions within range
    Given a sensor with range <range>
    And an object is placed at [<obj_x>, <obj_y>, <obj_z>]
    When the sensor scans
    Then the object should be detected

    Examples:
      | range | obj_x | obj_y | obj_z |
      | 1.0   | 0.5   | 0     | 0     |
      | 1.0   | 0     | 0.5   | 0     |
      | 1.0   | 0     | 0     | 0.5   |
      | 2.0   | 1.5   | 0     | 0     |
      | 2.0   | 0     | 1.5   | 1.0   |
      | 0.5   | 0.4   | 0     | 0     |
	  
  @object_detection_negative
  Scenario Outline: Sensor does not detect objects out of range
    Given a sensor with range <range>
    And an object is placed at [<obj_x>, <obj_y>, <obj_z>]
    When the sensor scans
    Then the object should not be detected

    Examples:
      | range | obj_x | obj_y | obj_z |
      | 1.0   | 1.5   | 0     | 0     |
      | 1.0   | 0     | 1.5   | 0     |
      | 0.5   | 0     | 0     | 1.0   |
