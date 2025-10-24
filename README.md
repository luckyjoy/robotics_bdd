# 🤖 Robotics BDD Framework

## 🧠 Overview

A Behavior-Driven Development (BDD) testing framework that integrates **Robot Framework**, **Allure Reporting**, and **Kubernetes (K8s)** orchestration for scalable, 
production-grade CI/CD automation and K8 execution with Docker.

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

## ⚙️ Setup Instructions

### 1. Local Environment Setup

```bash
git clone https://github.com/<your-org>/robotics-bdd-framework.git
cd robotics-bdd-framework
pip install -r requirements.txt
pytest --alluredir=allure-results
allure serve allure-results
```

### 2. Run with Docker

```bash
docker build -t robotics-bdd:latest .
docker run --rm -v $(pwd)/reports:/reports robotics-bdd:latest
```

### 3. Run in CI/CD

Use the provided scripts for pipeline execution:

```bash
# On Linux
docker-compose -f docker-compose.yml up --build --abort-on-container-exit

# On Windows
ci.bat
```

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

The CI pipeline will automatically attach and publish the generated reports as artifacts.

---

## 🧱 Project Structure

```
robotics-bdd-framework/
├── tests/                     # Robot Framework tests
├── resources/                 # Shared keywords and variables
├── supports/                  # Custom Python libraries and hooks
├── docker/                    # Dockerfiles and entrypoints
├── k8s/                       # Kubernetes manifests
├── reports/                   # Allure and log outputs
└── ci.bat / ci.sh             # Cross-platform CI entry points
```

---

## 🧩 Contributing

1. Fork the repository
2. Create a new branch (`feature/awesome-enhancement`)
3. Commit your changes
4. Open a Pull Request

---

## 🧑‍💻 Author

* **Author:** Bang Thien Nguyen ontario1998@gmail.com

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
