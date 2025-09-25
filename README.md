# Robot Simulation BDD Testing

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![BDD](https://img.shields.io/badge/BDD-FF5733?style=for-the-badge&logo=bdd&logoColor=white)

**Author:** Bang Thien Nguyen – ontario1998@gmail.com

This project uses **Behavior-Driven Development (BDD)** with `pytest-bdd` to test the functionality and safety of a simple robot simulation. Tests are written in **Gherkin syntax** and designed to be human-readable for both technical and non-technical team members.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- `pip` for package installation

### Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd robotics_bdd

    Install dependencies:

pip install -r requirements.txt

📋 Framework Structure

robotics_bdd/
├─ README.md
├─ Jenkinsfile
├─ allure-results/           # Allure raw results
├─ conftest.py
├─ environment.py
├─ environment.properties
├─ metadata.json
├─ pytest.ini
├─ requirements.txt
├─ run_all_tests.py
├─ simulation/
│  ├─ __init__.py
│  ├─ robot_sim.py           # Robot simulation logic
│  └─ sensors.py             # Sensor & Kalman filter logic
├─ steps/
│  ├─ __init__.py
│  ├─ navigation_steps.py
│  ├─ pick_and_place_steps.py
│  ├─ safety_steps.py
│  ├─ sensor_steps.py
│  └─ walking_steps.py
└─ features/
   ├─ navigation.feature
   ├─ pick_and_place.feature
   ├─ safety.feature
   ├─ sensors.feature
   └─ walking.feature

🏷️ BDD Test Tags

    navigation – Tests related to robot navigation

    pick_and_place – Tests for pick and place sequences

    safety – Safety-related tests

    walking – Walking-related tests

    sensors – Sensor-related tests

Example: Run only navigation tests

pytest -m "navigation"

Combine multiple tags:

pytest -m "pick_and_place and safety"

▶️ Running the Tests

Run all tests:

pytest --verbose

Run specific tag:

pytest -m sensors --verbose

📊 HTML Reporting with Allure
Step 1: Run tests and save results

pytest -m sensors --alluredir=allure-results

Step 2: Serve interactive HTML report

allure serve allure-results

    Opens an interactive report in the browser with test graphs, trends, and details.

Optional: Generate static HTML report

allure generate allure-results -o allure-report --clean

Open the report in browser:

start allure-report\index.html   # Windows
# or
open allure-report/index.html    # macOS/Linux


📊 HTML Reporting with pytest_html Report
pytest --html=reports/report.html --self-contained-html --capture=tee-sys


📝 Test Features
Navigation

Tests to ensure the robot moves safely to target positions, avoids obstacles, and follows waypoints.
Pick and Place

Tests covering object manipulation, arm reach limitations, and pick & place sequences while walking.
Safety

Comprehensive tests verifying safety protocols, preventing collisions, enforcing limits, and handling unexpected failures.
Walking

Tests for walking-related behaviors, including speed, posture, and movement transitions.
Sensor Fusion

Tests for the accuracy and convergence of the Kalman filter, ensuring reliable sensor-based position estimates.

