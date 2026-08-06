pipeline {
    agent any

    environment {
        AWS_REGION       = 'ap-south-1'                                  // change to your region
        AWS_ACCOUNT_ID   = '705822375785'                                // change to your AWS account ID
        ECR_REPO_NAME    = 'flask-cicd-app'
        ECR_REPO_URI     = "${"705822375785.dkr.ecr.ap-south-1.amazonaws.com/flask-app-repo"}"
        IMAGE_TAG        = "${BUILD_NUMBER}"                             // unique tag per build
        DEPLOY_EC2_IP    = '65.2.83.18'                                     // change to your deploy EC2 public IP
        DEPLOY_SSH_CREDS = 'ec2-ssh-key'                                 // Jenkins credentials ID for SSH key
        CONTAINER_NAME   = 'flask-app'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/praful0419/Flask-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${ECR_REPO_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Login to ECR') {
            steps {
                sh """
                    aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                """
            }
        }

        stage('Tag & Push to ECR') {
            steps {
                sh """
                    docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_REPO_URI}:${IMAGE_TAG}
                    docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_REPO_URI}:latest
                    docker push ${ECR_REPO_URI}:${IMAGE_TAG}
                    docker push ${ECR_REPO_URI}:latest
                """
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: ["${DEPLOY_SSH_CREDS}"]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@${DEPLOY_EC2_IP} '
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com &&
                            docker pull ${ECR_REPO_URI}:latest &&
                            docker stop ${CONTAINER_NAME} || true &&
                            docker rm ${CONTAINER_NAME} || true &&
                            docker run -d --name ${CONTAINER_NAME} -p 5000:5000 ${ECR_REPO_URI}:latest
                        '
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sh """
                    sleep 5
                    curl -f http://${DEPLOY_EC2_IP}:5000/health || exit 1
                """
            }
        }
    }

    post {
        success {
            echo "Deployment successful: ${ECR_REPO_URI}:${IMAGE_TAG}"
        }
        failure {
            echo "Pipeline failed — check logs above."
        }
    }
}
