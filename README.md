# 🤖 Robotics Behavior-Driven Development (BDD) Framework

A robust, BDD-driven framework for validating the functionality, path planning, and critical safety protocols of simulated mobile manipulator robots.

---

## 👤 Author & Contact  
**Author:** Bang Thien Nguyen  
**Contact:** ontario1998@gmail.com  

---

## 💡 Project Overview  
This framework implements **Behavior-Driven Development (BDD)** using `pytest-bdd` to create **living documentation** and validation for robot control logic.  
All requirements are defined as **human-readable Gherkin scenarios (Given–When–Then)**, ensuring clear collaboration between developers, QA, and stakeholders.

| **Component** | **Technology** | **Role** |
|----------------|----------------|-----------|
| Test Syntax | **Gherkin (.feature)** | Defines human-readable scenario-based test cases. |
| Test Runner | **pytest** | Industry-standard Python test execution framework. |
| BDD Integration | **pytest-bdd** | Maps Gherkin steps to Python step definitions. |
| Reporting | **Allure / pytest-html** | Generates professional, interactive test reports. |

---

## 🚀 Getting Started  

### 🔧 Prerequisites  
- 🐋 Docker Desktop *(required for containerized execution)*  
- 💻 Windows Command Prompt *(to run `run_docker.bat`)*  
- 🐍 (Optional) Python 3.10+ *(for local testing)*  
- 📈 (Optional) Allure command-line tool *(for local report viewing)*  

---

### ⚙️ Installation  

Clone the repository:  
```bash
git clone https://github.com/luckyjoy/robotics_bdd.git
cd robotics_bdd
```

Install dependencies (only if running outside Docker):  
```bash
pip install -r requirements.txt
```

---

## 🐳 Dockerized Execution (Recommended)

Ensure consistent results by running the full suite inside Docker.

### 🧱 Docker Image  
Image: **`robotics-bdd-local:latest`** — based on `python:3.10-slim`, includes:  
- Java JRE 21 + Allure CLI for reporting  
- Preinstalled dependencies from `requirements.txt`  
- `/app` as working directory

### ▶️ Run Tests via Script  
Use the included Windows batch file to automate build, test, and report steps.

**Script:** `run_docker.bat`  
**Workflow:**  

| **Step** | **Description** |
|-----------|-----------------|
| 1️⃣ Check Docker | Verifies Docker Desktop is active. |
| 2️⃣ Clean Up | Removes old `allure-results` and `reports` directories. |
| 3️⃣ Build / Pull | Builds or updates the Docker image. |
| 4️⃣ Execute Tests | Runs BDD tests (e.g., navigation) and stores results. |
| 5️⃣ Generate Report | Produces Allure HTML output. |
| 6️⃣ Serve Report | Opens Allure report locally on **http://localhost:8080**. |

Command to execute:  
```bash
run_docker.bat
```

---

### 🧹 Build Optimization – `.dockerignore` Example  

```
# Python artifacts
__pycache__
*.pyc
*.pyo
.pytest_cache
venv/
.tox/

# IDE/OS files
.vscode
.idea
.DS_Store
*.swp

# Generated reports/logs
/allure-results
/reports
*.log
```

---

## 🌳 Framework Architecture  

```
robotics_bdd/
├─ README.md
├─ run_docker.bat
├─ Dockerfile
├─ .dockerignore
├─ Jenkinsfile
├─ pytest.ini
├─ requirements.txt
├─ features/                  # Gherkin feature files
├─ steps/                     # Python step definitions
├─ src/                       # Simulation and robot logic
├─ supports/                  # Configs, test data, allure metadata
```

---

## 🏷️ Test Tags & Execution  

| **Tag** | **Focus Area** | **Description** |
|----------|----------------|-----------------|
| `navigation` | Path Planning | Safe movement, obstacle avoidance, waypoint following. |
| `pick_and_place` | Manipulation | Object handling, kinematics, and dynamic interactions. |
| `safety` | System Integrity | Collision prevention, boundary constraints, error handling. |
| `walking` | Gait Control | Posture, speed, stability, locomotion transitions. |
| `sensors` | Data Fusion | Sensor accuracy and Kalman Filter convergence. |

### 🧪 Run Tests Locally (Without Docker)  

| **Mode** | **Command** |
|-----------|-------------|
| Run All Tests | `pytest --verbose` |
| Run by Tag | `pytest -m sensors --verbose` |
| Sequential (OR) | `pytest -m "navigation or pick_and_place"` |
| Parallel | `pytest -m "navigation or safety" -n auto` |

---

## 📊 Professional Test Reporting  

### 1️⃣ **Interactive Allure Report (Recommended)**  
```bash
pytest -m "pick_and_place or safety" --alluredir=allure-results
allure serve allure-results
```
> Opens an interactive HTML dashboard with detailed execution insights.

### 2️⃣ **Static HTML Report (pytest-html)**  
```bash
pytest --html=reports/report.html --self-contained-html
```

---

## 📝 Test Coverage Summary  

| **Feature Area** | **Objective** | **Value Proposition** |
|-------------------|---------------|------------------------|
| Navigation | Validate robust, collision-free movement. | Reliable, safe path planning. |
| Pick and Place | Verify precise manipulation and object handling. | Ensures stable and successful grasping. |
| Safety | Enforce operational safety boundaries. | Protects integrity and prevents damage. |
| Sensor Fusion | Confirm stable sensor-based state estimation. | Verifies consistent environment awareness. |
| Walking | Validate smooth and safe locomotion dynamics. | Prevents falls, ensures stability and control. |

---

**📁 Repository:** *Robotics BDD Framework*  
**🧠 Approach:** Behavior-Driven Development (BDD)  
**📈 Reporting:** Allure + pytest-html  
**⚙️ CI/CD Integration:** Jenkins + Docker  
