pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Clone the Git repository
                checkout scm
            }
        }

        stage('Run Python Script') {
            steps {
                // Run the Python script
                echo "running .py file"
                sh 'python3 main.py'
                echo "completed"
            }
        }
    }
}