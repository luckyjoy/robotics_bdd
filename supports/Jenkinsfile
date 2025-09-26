pipeline {
    agent any

    environment {
        PYTHON = "python"
        ALLURE_RESULTS_DIR = "allure-results"
        ALLURE_REPORT_DIR = "allure-report-${env.BUILD_NUMBER}"
        // Dynamically use USERPROFILE for npm global bin
        PATH = "${env.PATH};${env.USERPROFILE}\\AppData\\Roaming\\npm"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out repository..."
                git branch: 'main', url: 'https://github.com/luckyjoy/robotics_bdd.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "Installing required Python packages..."
                bat "${PYTHON} -m pip install --upgrade pip"
                bat "${PYTHON} -m pip install pytest pytest-bdd allure-pytest"
                bat "npm install -g allure-commandline --force"
            }
        }

        stage('Run Pytest') {
            steps {
                echo "Running tests with Allure..."
                bat "if exist ${ALLURE_RESULTS_DIR} rd /s /q ${ALLURE_RESULTS_DIR}"
                bat "${PYTHON} -m pytest -m navigation --alluredir=${ALLURE_RESULTS_DIR}"
                echo "✅ All tests passed!"
            }
        }

        stage('Update environment.properties') {
            steps {
                script {
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
                    writeFile file: 'environment.properties', text: envProps
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                echo "Generating Robotics BDD Allure HTML report for Build #${env.BUILD_NUMBER}..."
                bat "if exist ${ALLURE_REPORT_DIR} rd /s /q ${ALLURE_REPORT_DIR}"
                bat "allure generate ${ALLURE_RESULTS_DIR} -o ${ALLURE_REPORT_DIR} --clean"
            }
        }

        stage('Archive & Publish Allure Report') {
            steps {
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

    post {
        always {
            echo "Pipeline finished for Build #${env.BUILD_NUMBER}"
        }
    }
}
