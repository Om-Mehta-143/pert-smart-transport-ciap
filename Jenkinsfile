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
        ECR_REPO   = "821302803491.dkr.ecr.ap-southeast-2.amazonaws.com/pert-smart-transport-ciap"
        AWS_REGION = "ap-southeast-2"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${params.BRANCH}", url: "${REPO_URL}"
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

        stage('Push to AWS ECR') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        if which ecr-login > /dev/null 2>&1; then
                            ecr-login ${AWS_REGION}
                        else
                            aws ecr get-login-password --region ${AWS_REGION} \
                              | docker login --username AWS --password-stdin ${ECR_REPO}
                        fi
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${ECR_REPO}:${IMAGE_TAG}
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${ECR_REPO}:latest
                        docker push ${ECR_REPO}:${IMAGE_TAG}
                        docker push ${ECR_REPO}:latest
                    '''
                }
            }
        }
    }
}
