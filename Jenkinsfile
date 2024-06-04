pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'moose3345/simple-note-app:latest'
        GIT_CREDENTIALS_ID = 'Github_Account'
    }
    stages {
        stage ('Checkout repo'){
            steps{
                script {
                    // Gunakan kredensial GitHub untuk meng-clone repository
                    withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS_ID}", passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                        git url: 'https://github.com/mahaputrailhamawal/simple-note-app.git', branch: 'main', credentialsId: "${GIT_CREDENTIALS_ID}"
                    }
                }
            }
        }
        stage ('Build'){
            steps {
                script{
                // build docker image from dockerfile
                sh 'docker build -t $DOCKER_IMAGE ./app'
                }
            }
        }

        stage ('Deploy with Docker Compose'){
            steps {
                script{
                    sh 'docker compose -f docker-compose.yaml up -d --build'
                }
            }
        }
    }
}