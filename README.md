# 🤖 Robotics Behavior-Driven Development (BDD) Framework

A robust, BDD-driven framework for validating the functionality, path planning, and critical **safety protocols** of a simulated mobile manipulator robot.

**Author:** Bang Thien Nguyen | **Contact:** ontario1998@gmail.com

-----

## 💡 Project Overview

This framework implements **Behavior-Driven Development (BDD)** using `pytest-bdd` to create a **living documentation** and validation layer for the robot's control logic. All requirements are documented as human-readable **Gherkin scenarios** (Given-When-Then), ensuring clear collaboration between technical and non-technical stakeholders.

| Core Component | Technology | Role |
| :--- | :--- | :--- |
| **Test Syntax** | **Gherkin** (`.feature` files) | Defines test cases using unambiguous scenario descriptions. |
| **Test Runner** | **`pytest`** | Industry-standard Python testing tool. |
| **BDD Integration** | **`pytest-bdd`** | Maps Gherkin steps to executable Python code (step definitions). |
| **Reporting** | **Allure & `pytest-html`** | Generates professional, interactive HTML reports for test traceability. |

-----

## 🚀 Getting Started

### Prerequisites

  * Python 3.8+
  * `pip` package manager
  * Allure command-line tool (required for full HTML reporting)

### Installation

1.  **Clone the Repository:**

    ```bash
    git clone <your-repository-url>
    cd robotics_bdd
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

-----

## 🌳 Framework Architecture

The structure enforces separation between simulation logic, feature specifications, and executable code.

```
robotics_bdd/
├─ README.md
├─ Jenkinsfile                      # CI/CD pipeline definition
├─ pytest.ini                       # pytest configuration (markers)
├─ requirements.txt
├─ simulation/
│  ├─ robot_sim.py                  # Core robot model and simulation API
│  └─ sensors.py                    # Sensor/Kalman filter logic
├─ features/                        # Gherkin Scenarios
│  ├─ navigation.feature
│  ├─ pick_and_place.feature
│  ├─ safety.feature
│  ├─ sensors.feature
│  └─ walking.feature
└─ steps/                           # Python Step Definitions (Glue Code)
   ├─ navigation_steps.py
   ├─ pick_and_place_steps.py
   ├─ safety_steps.py
   ├─ sensor_steps.py
   └─ walking_steps.py
```

-----

## 🏷️ Test Tags and Execution

Tests are grouped using `pytest` markers (tags) to allow for selective execution.

| Tag | Focus Area | Description |
| :--- | :--- | :--- |
| **`navigation`** | Path Planning | Safe movement, obstacle avoidance, and waypoint following. |
| **`pick_and_place`** | Manipulation | Object handling, arm kinematics, and dynamic manipulation sequences. |
| **`safety`** | System Integrity | Collision prevention, boundary limits, and critical error handling. |
| **`walking`** | Gait Control | Posture, speed, stability, and movement transitions during locomotion. |
| **`sensors`** | Data Fusion | Accuracy and convergence of sensor filtering (e.g., Kalman Filter). |

### Running Test Suites

| Execution Mode | Command |
| :--- | :--- |
| **Run All Tests** | `pytest --verbose` |
| **Run Specific Tag** | `pytest -m sensors --verbose` |
| **Sequential Execution (OR)** | `pytest -m "navigation or pick_and_place"` |
| **Parallel Execution (OR)** | `pytest -m "navigation or safety" -n auto` | Uses `pytest-xdist` to run tests across available CPU cores. |

-----

## 📊 Professional Test Reporting

### 1\. Interactive Allure Report (Recommended for Analysis)

Allure generates a rich, interactive HTML dashboard suitable for detailed test analysis, CI/CD integration, and trend monitoring.

1.  **Generate Raw Results:**
    ```bash
    pytest -m "pick_and_place or safety" --alluredir=allure-results
    ```
2.  **Serve Interactive Report:**
    ```bash
    allure serve allure-results
    ```
    *This opens the report in your default web browser.*

### 2\. Static HTML Report (`pytest-html`)

Generates a single, self-contained HTML file for simple archiving and sharing.

```bash
pytest --html=reports/report.html --self-contained-html
```

-----

## 📝 Test Coverage Summary

| Feature Area | Objective | Value Proposition |
| :--- | :--- | :--- |
| **Navigation** | Validate robust, collision-free movement across the environment. | Ensures the robot reliably reaches targets while adhering to safety clearances. |
| **Pick and Place** | Confirm reliable object interaction and arm dexterity within reach limits. | Guarantees consistent success rates for manipulation tasks. |
| **Safety** | Enforce non-negotiable operational limits and error handling. | Prevents equipment damage and maintains system integrity (e.g., chest height, boundary limits). |
| **Sensor Fusion** | Ensure the accuracy and stability of sensor-based state estimation. | Validates the integrity of the robot's perception system (Kalman Filter convergence). |
| **Walking** | Verify stable and safe locomotion dynamics. | Prevents tripping/falling and maintains optimal posture during movement. |

