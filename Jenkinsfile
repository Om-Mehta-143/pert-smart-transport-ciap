pipeline {
    agent any

    parameters {
        string(name: 'BRANCH', defaultValue: 'main', description: 'Git branch to build')
    }

    environment {
        IMAGE_NAME = "pert-smart-transport"
        IMAGE_TAG  = "v1"
        REPO_URL   = "https://github.com/Om-Mehta-143/pert-smart-transport-ciap.git"
        SONAR_HOST = "http://sonarqube:9000"
        SONAR_KEY  = "pert-smart-transport-ciap"
        CONTAINER_NAME = "pert-app-prod"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${params.BRANCH}", url: "${REPO_URL}"
            }
        }

        stage('Unit Testing') {
            steps {
                sh 'python3 -m unittest test_pert.py'
            }
        }

        stage('SonarQube Scan') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        sonar-scanner \
                          -Dsonar.host.url="${SONAR_HOST}" \
                          -Dsonar.token="${SONAR_TOKEN}" \
                          -Dsonar.login="${SONAR_TOKEN}" \
                          -Dsonar.projectKey="${SONAR_KEY}" \
                          -Dsonar.sources="." \
                          -Dsonar.inclusions="app.py,pert_engine.py,static/**,templates/**" \
                          -Dsonar.exclusions="venv/**,terraform/**" || true
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .'
            }
        }

        stage('Trivy Scan') {
            steps {
                script {
                    sh '''
                        curl -fsSL -o html.tpl https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl || true
                        trivy image \
                          --severity HIGH,CRITICAL \
                          --format template \
                          --template "@html.tpl" \
                          -o trivy-report.html \
                          ${IMAGE_NAME}:${IMAGE_TAG} || true
                    '''

                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'trivy-report.html',
                        reportName: 'Trivy Scan Report'
                    ])
                }
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p 5000:5000 ${IMAGE_NAME}:${IMAGE_TAG}
                    sleep 3
                    docker ps --filter "name=${CONTAINER_NAME}"
                '''
            }
        }
    }
}
