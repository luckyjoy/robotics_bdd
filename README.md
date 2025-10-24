# 🤖 Robotics BDD Framework

## 🧠 Overview

A Behavior-Driven Development (BDD) testing framework that integrates **Robot Framework**, **Allure Reporting**, and **Kubernetes (K8s)** orchestration for scalable, production-grade CI/CD automation.

This repository enables automation teams to:

* Write human-readable test cases with **Gherkin syntax**.
* Run tests locally or in **distributed cloud-native environments**.
* Automatically generate and host **interactive Allure reports**.
* Integrate with **Docker** and **Kubernetes Jobs** for high scalability.

---

## 🧩 Key Features

* **Robot Framework + Allure** for structured, visual, and traceable test reporting.
* **Cross-platform CI/CD**: Works on Windows (ci.bat) and Linux (ci.sh) agents.
* **Dockerized Test Execution** ensures consistency and easy environment setup.
* **Kubernetes Integration** to offload workloads to production-like clusters.
* **GitHub Actions / Jenkins** support for CI/CD pipelines.

---


## 🏷️ Test Tags & Execution  

| **Tag** | **Focus Area** | **Description** |
|----------|----------------|-----------------|
| `navigation` | Path Planning | Safe movement, obstacle avoidance, waypoint following. |
| `pick_and_place` | Manipulation | Object handling, kinematics, and dynamic interactions. |
| `safety` | System Integrity | Collision prevention, boundary constraints, error handling. |
| `walking` | Gait Control | Posture, speed, stability, locomotion transitions. |
| `sensors` | Data Fusion | Sensor accuracy and Kalman Filter convergence. |


---


## ⚙️ Setup Instructions

### 1. Local Environment Setup

```bash
git clone https://github.com/<your-org>/robotics-bdd-framework.git
cd robotics-bdd-framework
pip install -r requirements.txt
pytest --alluredir=allure-results
allure serve allure-results
```

### 2. Run Tests Locally (Without Docker)  

| **Mode** | **Command** |
|-----------|-------------|
| Run All Tests | `pytest --verbose` |
| Run by Tag | `pytest -m sensors --verbose` |
| Sequential (OR) | `pytest -m "navigation or pick_and_place"` |
| Parallel | `pytest -m "navigation or safety" -n auto` |


### 3. Run with Docker

```bash
docker build -t robotics-bdd:latest .
docker run --rm -v $(pwd)/reports:/reports robotics-bdd:latest

or python run_docker.py <build_number> [test_suite]

```

### 3.️ CI/CD Integration

| System                   | Description                                 |
| ------------------------ | ------------------------------------------- |
| **Jenkinsfile**          | Automates build → test → report             |
| **GitHub Actions**       | Easily adaptable for cloud CI/CD            |
| **Allure + pytest**      | Generates professional analytics dashboards |
| **Dockerized Execution** | Guarantees repeatable test environments     |

📁 **Repository:** Robotics BDD Framework
🧠 **Approach:** Behavior-Driven Development (BDD)
📈 **Reporting:** Allure + pytest-html
⚙️ **CI/CD Integration:** Jenkins/GitHub + Docker/K8s
📈 **Example CI/CD Badges**

---

## 🌐 Advanced CI/CD: Docker and Kubernetes (K8s) Integration

This framework leverages a sophisticated pipeline (`kubernetes_pipeline.bat` or `ci.bat`) to ensure reliability and scalability for running tests in a production-like environment.

### 1. Component Roles

| Component                 | Purpose in the Pipeline                                                                                          | Key Benefit                                                                                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Docker**                | Packages the Robot Framework tests, Python dependencies, and tools into a single, isolated image.                | **Consistency**: Guarantees tests run the exact same way on every machine or cluster node.                                                         |
| **Kubernetes (K8s) Job**  | Executes the BDD Test Docker image as a controlled workload on a cluster.                                        | **Reliability & Scalability**: Decouples heavy test execution from the CI runner, using robust K8s infrastructure to manage resources and retries. |
| **Report Artifact Image** | Packages the final static Allure HTML report into a small Nginx web server image, which is pushed to Docker Hub. | **Portable Publishing**: Creates a web-hosted artifact deployable anywhere for easy remote viewing and sharing.                                    |

### 2. K8s Execution Flow

K8s execution refers to running the BDD Test container directly on a Kubernetes cluster. This is achieved via a Job object defined in `robotics-bdd-job.yaml`.

* **Job Object**: The Kubernetes Job ensures that the specific task (running the BDD tests) is executed to completion. If the test Pod fails due to infrastructure issues, the Job can be configured to automatically retry the test container.
* **Decoupling**: The pipeline instructs the cluster to run the job (`kubectl apply`), and Kubernetes handles the entire execution, from finding a suitable node to pulling the image and monitoring the test run.

```bash

kubenestes_pipeline.bat <build_number> [test_suite]

```
### 3. Remote Report Access

After the tests run, the final Report Artifact Image (`luckyjoy/robotics-bdd-report:<BUILD_NUMBER>`) is published to Docker Hub.

To view the report remotely, run this image on any publicly accessible server:

```bash
# On your remote server/VM with Docker installed:
docker run -d -p 80:80 docker.io/luckyjoy/robotics-bdd-report:<BUILD_NUMBER>

# Access via browser:
http://<YOUR_SERVER_PUBLIC_IP_OR_DNS_NAME>
```

---

## 📊 Allure Reporting

To generate and serve the Allure Report locally:

```bash
pytest --alluredir=allure-results
allure generate allure-results --clean -o allure-report
allure open allure-report
```

📸 *Preview:* 

![Allure Overview Report](https://github.com/luckyjoy/robotics_bdd/blob/main/reports/allure_report.jpg)


![Allure Pytest Suites Report](https://github.com/luckyjoy/robotics_bdd/blob/main/reports/allure_suites.jpg)

> Opens an interactive HTML dashboard locally with detailed execution insights.

> The CI pipeline will automatically attach and publish the generated reports as artifacts.

---

## 🧱 Project Structure

```
robotics_bdd/
├─ BUILD_NUMBER.txt           # File storing current build number.
├─ Dockerfile                 # Defines the BDD Test Docker image (runtime environment).
├─ Jenkinsfile                # CI/CD pipeline definition for Jenkins.
├─ README.md
├─ requirements.txt			  # dependencies requirements
├─ run_docker.py			  # python script to run tests insie docker container.
├─ run_kubenestes.py          # Python script to orchestrate K8s jobs and report generation.
├─ kubenestes_pipeline.bat    # CI execution script.
├─ robotics-bdd-job.yaml      # Kubernetes Job definition (runs the tests).
├─ robotics-bdd-pv.yaml       # Kubernetes Persistent Volume definition.
├─ robotics-bdd-pvc.yaml      # Kubernetes Persistent Volume Claim.
│
├─ features/                  # Gherkin feature files
│  └─ manual_tests/
│
├─ steps/                     # Python step definitions (pick_and_place_steps.py, navigation_steps.py, etc.)
│
├─ simulation/                # Robot simulation and core logic (robot_sim.py, sensors.py)
│
├─ reports/                   # Static report files
│  └─ allure-report/          # Final HTML report files
│     └─ Dockerfile           # Dockerfile for packaging the final report as a web server
│
└─ allure-results/            # Raw JSON/XML results (generated during test execution)

---

## 🧩 Contributing

1. Fork the repository
2. Create a new branch (`feature/awesome-enhancement`)
3. Commit your changes
4. Open a Pull Request

---

## 🧑‍💻 Maintainers

* **Author:** Bang Thien Nguyen - ontario1998@gmail.com


---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
