pipeline {
    agent any

    environment {
        PYTHON_EXE = "python"
        ALLURE_RESULTS_DIR = "allure-results"
        ALLURE_REPORT_DIR = "allure-report-latest"        // report folder per build
        ALLURE_HISTORY_DIR = "C:\\ProgramData\\Jenkins\\.jenkins\\jobs\\robotics_bdd\\allure-history"
        ALLURE_HISTORY_TEMP = "history_temp_dir"
        PATH = "${env.PATH};${env.USERPROFILE}\\AppData\\Roaming\\npm"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/luckyjoy/robotics_bdd.git', branch: 'main'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing required packages...'
                bat """
                    "${PYTHON_EXE}" -m pip install --upgrade pip
                    "${PYTHON_EXE}" -m pip install pytest pytest-bdd allure-pytest
                    npm install -g allure-commandline --force
                """
            }
        }

        stage('Load Allure History') {
            steps {
                script {
                    echo "Restoring Allure history..."
                    bat "if exist ${ALLURE_RESULTS_DIR} rd /s /q ${ALLURE_RESULTS_DIR}"
                    bat "mkdir ${ALLURE_RESULTS_DIR}"

                    // Copy previous history if exists
                    bat """
                        if exist ${ALLURE_HISTORY_DIR} xcopy /E /I /Y ${ALLURE_HISTORY_DIR} ${ALLURE_RESULTS_DIR}\\history
                    """
                }
            }
        }

        stage('Run Pytest') {
            steps {
                echo "Running tests with Allure..."
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    bat """
                        "${PYTHON_EXE}" -m pytest -m navigation --alluredir=${ALLURE_RESULTS_DIR} --capture=tee-sys
                    """
                }
                echo "Tests execution complete."
            }
        }

        stage('Add Allure Metadata') {
            steps {
                script {
                    echo 'Adding Allure metadata...'

                    def categoriesJson = """[
                        {
                            "name": "Safety Protocol Violation (Hard Stop)",
                            "messageRegex": ".*(ArmError|SafetyViolation|chest height|boundary|RuntimeError: No arm).*",
                            "description": "Failures indicating the robot attempted an unsafe operation.",
                            "matchedStatuses": ["failed", "broken"]
                        },
                        {
                            "name": "Core Logic / Navigation Defect",
                            "messageRegex": ".*(AssertionError|not approximately|less than|greater than|final position).*",
                            "description": "Standard BDD assertion failures.",
                            "matchedStatuses": ["failed"]
                        },
                        {
                            "name": "Simulation Environment or Stability Issue",
                            "messageRegex": ".*(Timeout|ConnectionError|simulated_robot initialization failed).*",
                            "traceRegex": ".*(PyBullet|Gazebo|mocked gripper).*",
                            "description": "Failures related to the simulation engine or hardware connection errors.",
                            "matchedStatuses": ["broken"]
                        }
                    ]"""
                    writeFile file: "${ALLURE_RESULTS_DIR}/categories.json", text: categoriesJson.stripIndent()

                    def executorJson = """{
                        "name": "Robotics BDD Framework Runner",
                        "type": "CI_Pipeline",
                        "url": "${env.JENKINS_URL}",
                        "buildOrder": "${env.BUILD_ID}",
                        "buildName": "Robotics BDD #${env.BUILD_ID}",
                        "buildUrl": "${env.BUILD_URL}",
                        "reportUrl": "${env.BUILD_URL}Robotics-BDD-Allure-Report-Build-${env.BUILD_NUMBER}/index.html",
                        "data": {
                            "Validation Engineer": "TBD",
                            "Product Model": "BDD-Sim-PyBullet",
                            "Test Framework": "pytest-bdd"
                        }
                    }"""
                    writeFile file: "${ALLURE_RESULTS_DIR}/executor.json", text: executorJson.stripIndent()

                    def envProps = """Project=Robotics BDD Simulation Framework
Author=Bang Thien Nguyen
Email=ontario1998@gmail.com
Robot Model=Gazebo_Pioneer3DX
Simulation Engine=PyBullet
Operating System=Windows 11
Python Version=3.10.12
Framework Version=1.0.0
Test Type=Integration
HTML Reporter=Allure Test Report 2.35.1
Build Number=${env.BUILD_NUMBER}
"""
                    writeFile file: "${ALLURE_RESULTS_DIR}/environment.properties", text: envProps.stripIndent()
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                echo "Generating Allure HTML report..."
                bat """
                    if exist ${ALLURE_REPORT_DIR} rd /s /q ${ALLURE_REPORT_DIR}
                    allure generate ${ALLURE_RESULTS_DIR} -o ${ALLURE_REPORT_DIR} --clean
                """

                // Copy history to central folder for trend charts
                bat """
                    if exist ${ALLURE_REPORT_DIR}\\history (
                        xcopy /E /I /Y ${ALLURE_REPORT_DIR}\\history ${ALLURE_HISTORY_DIR}
                    )
                """
            }
        }

        stage('Archive & Publish Allure Report') {
            steps {
                script {
                    echo 'Archiving and publishing Allure report...'

                    archiveArtifacts artifacts: "${ALLURE_REPORT_DIR}/**/*", allowEmptyArchive: true

                    publishHTML(target: [
                        reportName: "Robotics-BDD-Allure-Report-Build-${env.BUILD_NUMBER}",
                        reportDir: "${ALLURE_REPORT_DIR}",
                        reportFiles: "index.html",
                        keepAll: true,
                        alwaysLinkToLastBuild: true
                    ])
                }
            }
        }
    }

    post {
        always {
            cleanWs()
            echo "Pipeline finished."
        }
    }
}
