pipeline {
    agent any

    environment {
        IMAGE_NAME = 'jinwooarise/pert-smart-transport'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        DOCKER_HUB_CRED = 'dockerhub-credentials'
        SONAR_SERVER_NAME = 'SonarQube'
        CONTAINER_NAME = 'pert-app-prod'
        HOST_PORT = '5000'
    }

    options {
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo 'Checking out source repository...'
                checkout scm
            }
        }

        stage('Build & Test') {
            steps {
                echo 'Setting up Python virtual environment and running unit tests...'
                sh '''
                    python3 -m venv venv || python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest --verbose test_pert.py
                '''
            }
        }

        stage('SonarQube Static Analysis') {
            steps {
                echo 'Executing SonarQube Scanner code quality and security analysis...'
                withSonarQubeEnv("${SONAR_SERVER_NAME}") {
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=pert-smart-transport-ciap \
                            -Dsonar.sources=. \
                            -Dsonar.inclusions=app.py,pert_engine.py,static/**,templates/** \
                            -Dsonar.exclusions=venv/**,terraform/** \
                            -Dsonar.tests=. \
                            -Dsonar.test.inclusions=test_pert.py
                    '''
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    script {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Pipeline aborted: SonarQube Quality Gate failure status: ${qg.status}"
                        }
                    }
                }
            }
        }

        stage('Trivy Filesystem Vulnerability Scan') {
            steps {
                echo 'Running Trivy FS scan for vulnerable dependencies...'
                sh '''
                    trivy fs \
                        --severity HIGH,CRITICAL \
                        --format table \
                        --output trivy-fs-report.txt \
                        .
                    cat trivy-fs-report.txt
                '''
            }
        }

        stage('Docker Image Build') {
            steps {
                echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG} and ${IMAGE_NAME}:latest..."
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Trivy Container Image Scan') {
            steps {
                echo "Scanning Docker image ${IMAGE_NAME}:${IMAGE_TAG} with Trivy..."
                sh """
                    trivy image \
                        --severity HIGH,CRITICAL \
                        --format table \
                        --output trivy-image-report.txt \
                        ${IMAGE_NAME}:${IMAGE_TAG}
                    cat trivy-image-report.txt
                """
            }
        }

        stage('Docker Hub Push') {
            steps {
                echo 'Pushing hardened image to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: "${DOCKER_HUB_CRED}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
                        docker logout
                    """
                }
            }
        }

        stage('Automated Deployment') {
            steps {
                echo 'Deploying application container with health monitoring...'
                sh """
                    # Stop and remove any pre-existing instance
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true

                    # Run new container instance
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart unless-stopped \
                        -p ${HOST_PORT}:5000 \
                        ${IMAGE_NAME}:latest

                    # Verify health check
                    sleep 5
                    curl -f http://localhost:${HOST_PORT}/healthz || (docker logs ${CONTAINER_NAME} && exit 1)
                """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'trivy-*.txt', allowEmptyArchive: true
            echo 'Build completed. Archiving scan results...'
        }
        success {
            echo "CI/CD Pipeline finished successfully for build ${env.BUILD_NUMBER}."
        }
        failure {
            echo "Pipeline FAILED on build ${env.BUILD_NUMBER}. Review stage logs."
        }
        cleanup {
            cleanWs()
        }
    }
}
