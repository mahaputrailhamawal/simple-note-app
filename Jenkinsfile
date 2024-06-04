pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'moose3345/simple-note-app:latest'
    }
    stages {
        stage ('Checkout repo'){
            steps{
                //Clone the repository
                echo 'Clone repository'
                git url: 'https://github.com/mahaputrailhamawal/simple-note-app.git', branch: 'main'
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
                    sh 'docker-compose -f docker-compose.yaml up -d --build'
                }
            }
        }
    }
}