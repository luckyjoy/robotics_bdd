pipeline {
    agent any

    environment {
        PYTHON_EXE = "python"
        ALLURE_RESULTS_DIR = "allure-results"
        LINUX_ALLURE_RESULTS_DIR = "linux-allure-results"
        ALLURE_REPORT_DIR = "allure-report-latest"
        ALLURE_HISTORY_DIR = "C:\\ProgramData\\Jenkins\\.jenkins\\jobs\\robotics_bdd\\allure-history"
        PATH = "${env.PATH};${env.USERPROFILE}\\AppData\\Roaming\\npm"
        DOCKER_IMAGE = "python:3.10-slim"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout Source Code') {
            steps {
                timestamps {
                    git branch: 'main', url: 'https://github.com/luckyjoy/robotics_bdd.git'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                timestamps {
                    script {
                        if (!isUnix()) {
                            echo "Installing Windows dependencies..."
                            bat """
                                "%PYTHON_EXE%" -m pip install --upgrade pip
                                if exist requirements.txt "%PYTHON_EXE%" -m pip install -r requirements.txt
                                npm install -g allure-commandline --force
                                where allure >nul 2>nul || (echo Allure CLI not found on PATH & exit /b 1)
                            """
                        } else {
                            echo "Installing Linux dependencies..."
                            sh '''
                                set -e
                                pip install -q pytest allure-pytest
                            '''
                        }
                    }
                }
            }
        }

        stage('Restore Allure History') {
            steps {
                timestamps {
                    script {
                        def resultsDir = isUnix() ? LINUX_ALLURE_RESULTS_DIR : ALLURE_RESULTS_DIR
                        if (!isUnix()) {
                            bat """
                                if exist "%ALLURE_RESULTS_DIR%" rd /s /q "%ALLURE_RESULTS_DIR%"
                                mkdir "%ALLURE_RESULTS_DIR%"
                                if exist "%ALLURE_HISTORY_DIR%" xcopy /E /I /Y "%ALLURE_HISTORY_DIR%" "%ALLURE_RESULTS_DIR%\\history" >nul
                            """
                        } else {
                            sh """
                                rm -rf "${LINUX_ALLURE_RESULTS_DIR}"
                                mkdir -p "${LINUX_ALLURE_RESULTS_DIR}"
                                if [ -d "${ALLURE_HISTORY_DIR}" ]; then
                                    cp -r "${ALLURE_HISTORY_DIR}/." "${LINUX_ALLURE_RESULTS_DIR}/history" || true
                                fi
                            """
                        }
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                timestamps {
                    script {
                        if (!isUnix()) {
                            echo "Running Windows tests..."
                            catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                                bat "\"%PYTHON_EXE%\" -m pytest -m ^"security or pick or navigation or walking or safety"^ --alluredir=\"%ALLURE_RESULTS_DIR%\" --capture=tee-sys"
                            }
                        } else {
                            echo "Running Linux tests via Docker..."
                            catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                                sh '''
                                    set -e
                                    docker --version || (echo "Docker not found, skipping Docker tests." && exit 0)
                                    docker pull ${DOCKER_IMAGE}
                                    docker run --rm -v "$PWD:/tests" -w /tests ${DOCKER_IMAGE} bash -lc \
                                        "pip install -q pytest allure-pytest && pytest -m ^"security or pick or navigation or walking or safety^" --alluredir=/tests/${LINUX_ALLURE_RESULTS_DIR}"
                                '''
                            }
                        }
                    }
                }
            }
        }

        stage('Add Allure Metadata') {
            steps {
                timestamps {
                    script {
                        echo 'Adding Allure metadata...'

                        def categoriesJson = """[
                            {"name":"Safety Protocol Violation (Hard Stop)","messageRegex":".*(ArmError|SafetyViolation|chest height|boundary|RuntimeError: No arm).*","description":"Failures indicating the robot attempted an unsafe operation.","matchedStatuses":["failed","broken"]},
                            {"name":"Core Logic / Navigation Defect","messageRegex":".*(AssertionError|not approximately|less than|greater than|final position).*","description":"Standard BDD assertion failures.","matchedStatuses":["failed"]},
                            {"name":"Simulation Environment or Stability Issue","messageRegex":".*(Timeout|ConnectionError|simulated_robot initialization failed).*","traceRegex":".*(PyBullet|Gazebo|mocked gripper).*","description":"Failures related to the simulation engine or hardware connection errors.","matchedStatuses":["broken"]}
                        ]"""
                        writeFile file: "${ALLURE_RESULTS_DIR}/categories.json", text: categoriesJson

                        def executorJson = """{
                            "name": "Robotics BDD Framework Runner",
                            "type": "CI_Pipeline",
                            "url": "${env.JENKINS_URL}",
                            "buildOrder": "${env.BUILD_ID}",
                            "buildName": "Robotics BDD #${env.BUILD_ID}",
                            "buildUrl": "${env.BUILD_URL}",
                            "reportUrl": "${env.BUILD_URL}Robotics-BDD-Allure-Report-Build-${env.BUILD_NUMBER}/index.html",
                            "data": {"Validation Engineer":"TBD","Product Model":"BDD-Sim-PyBullet","Test Framework":"pytest"}
                        }"""
                        writeFile file: "${ALLURE_RESULTS_DIR}/executor.json", text: executorJson

                        def envProps = """Project=Robotics BDD Simulation Framework
Author=Bang Thien Nguyen
Robot Model=Gazebo_Pioneer3DX
Simulation Engine=PyBullet
Operating System=${isUnix() ? 'Linux' : 'Windows 11'}
Docker_Image_Name=robotics-runner
Docker_Build_Context=Repository Root (. )
Docker_Runtime_Environment=Run Linux Tests in Docker (PowerShell)
Python Version=3.10.12
Framework Version=1.0.0
Test Type=Integration
HTML Reporter=Allure Test Report 2.35.1
Build Number=${env.BUILD_NUMBER}
"""
                        writeFile file: "${ALLURE_RESULTS_DIR}/environment.properties", text: envProps
                    }
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                timestamps {
                    script {
                        echo "Generating Allure report..."
                        if (!isUnix()) {
                            bat """
                                if exist "%ALLURE_REPORT_DIR%" rd /s /q "%ALLURE_REPORT_DIR%"
                                mkdir "%ALLURE_REPORT_DIR%"
                                allure generate "%ALLURE_RESULTS_DIR%" "%LINUX_ALLURE_RESULTS_DIR%" -o "%ALLURE_REPORT_DIR%" --clean
                            """
                        } else {
                            sh '''
                                rm -rf "${ALLURE_REPORT_DIR}"
                                mkdir -p "${ALLURE_REPORT_DIR}"
                                allure generate "${ALLURE_RESULTS_DIR}" "${LINUX_ALLURE_RESULTS_DIR}" -o "${ALLURE_REPORT_DIR}" --clean || true
                            '''
                        }

                        // Persist Allure history
                        if (!isUnix()) {
                            bat """
                                if exist "%ALLURE_REPORT_DIR%\\history" (
                                    if not exist "%ALLURE_HISTORY_DIR%" mkdir "%ALLURE_HISTORY_DIR%"
                                    xcopy /E /I /Y "%ALLURE_REPORT_DIR%\\history" "%ALLURE_HISTORY_DIR%" >nul
                                )
                            """
                        } else {
                            sh '''
                                if [ -d "${ALLURE_REPORT_DIR}/history" ]; then
                                    mkdir -p "${ALLURE_HISTORY_DIR}" || true
                                    cp -r "${ALLURE_REPORT_DIR}/history" "${ALLURE_HISTORY_DIR}/" || true
                                fi
                            '''
                        }
                    }
                }
            }
        }

        stage('Archive & Publish Allure Report') {
            steps {
                timestamps {
                    script {
                        echo 'Archiving and publishing Allure report...'
                        archiveArtifacts artifacts: "${ALLURE_REPORT_DIR}/**/*", allowEmptyArchive: true

                        publishHTML(target: [
                            reportName: "Robotics-BDD-Allure-Report-Build-${env.BUILD_NUMBER}-CrossPlatform",
                            reportDir: "${ALLURE_REPORT_DIR}",
                            reportFiles: "index.html",
                            keepAll: true,
                            alwaysLinkToLastBuild: true
                        ])
                    }
                }
            }
        }
    }

    post {
        always {
            timestamps {
                echo "Report (if archived): ${env.BUILD_URL}artifact/${ALLURE_REPORT_DIR}/index.html"
                cleanWs()
                echo "Pipeline finished."
            }
        }
    }
}
