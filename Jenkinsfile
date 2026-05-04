pipeline {
    agent any

    environment {
        // ✅ Change this to your actual VM IP
        VM_IP   = "10.0.0.4"
        VM_PORT = "5000"
        APP_PID_FILE = "app.pid"
    }

    stages {

        // ════════════════════════════════════════════════
        // STAGE 1: Checkout Code from GitHub
        // ════════════════════════════════════════════════
        stage('📥 Checkout Code') {
            steps {
                echo '=== Checking out source code from GitHub ==='
                checkout scm
                echo '✅ Code checkout complete!'
            }
        }

        // ════════════════════════════════════════════════
        // STAGE 2: Setup Python Virtual Environment
        // ════════════════════════════════════════════════
        stage('🐍 Setup Python Environment') {
            steps {
                echo '=== Setting up Python virtual environment ==='
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
                echo '✅ Python environment ready!'
            }
        }

        // ════════════════════════════════════════════════
        // STAGE 3: Start Flask Application
        // ════════════════════════════════════════════════
        stage('🚀 Start Flask Application') {
            steps {
                echo '=== Starting Flask application ==='
                sh '''
                    # Kill any old instance if running
                    if [ -f ${APP_PID_FILE} ]; then
                        OLD_PID=$(cat ${APP_PID_FILE})
                        kill $OLD_PID 2>/dev/null || true
                        rm -f ${APP_PID_FILE}
                    fi

                    # Delete old database so tests start fresh
                    rm -f employees.db

                    # Start Flask app in the background
                    . venv/bin/activate
                    HOST=0.0.0.0 PORT=${VM_PORT} python3 app.py &

                    # Save the PID so we can stop it later
                    echo $! > ${APP_PID_FILE}

                    # Wait 5 seconds for Flask to fully start
                    sleep 5

                    echo "Flask app started with PID: $(cat ${APP_PID_FILE})"
                '''
                echo '✅ Flask app is running!'
            }
        }

        // ════════════════════════════════════════════════
        // STAGE 4: Verify Application is Accessible
        // ════════════════════════════════════════════════
        stage('🔍 Health Check') {
            steps {
                echo '=== Verifying application is accessible ==='
                sh '''
                    # Wait for the app to respond (retry up to 10 times)
                    for i in $(seq 1 10); do
                        if curl -sf http://${VM_IP}:${VM_PORT}/ > /dev/null; then
                            echo "✅ Application is UP at http://${VM_IP}:${VM_PORT}/"
                            break
                        fi
                        echo "Attempt $i: App not ready yet... waiting 3s"
                        sleep 3
                    done

                    # Final check — fail pipeline if app is still down
                    curl -sf http://${VM_IP}:${VM_PORT}/ || \
                      (echo "❌ App is not accessible! Failing pipeline." && exit 1)
                '''
            }
        }

        // ════════════════════════════════════════════════
        // STAGE 5: Run Selenium Tests
        // ════════════════════════════════════════════════
        stage('🧪 Run Selenium Tests') {
            steps {
                echo '=== Running Selenium tests with pytest ==='
                sh '''
                    . venv/bin/activate
                    pytest tests/test_app.py \
                        --tb=short \
                        -v \
                        --junit-xml=test-results.xml
                '''
                echo '✅ All tests passed!'
            }
        }
    }

    // ════════════════════════════════════════════════
    // POST: Always runs — cleanup + publish results
    // ════════════════════════════════════════════════
    post {
        always {
            echo '=== Cleaning up — stopping Flask app ==='
            sh '''
                if [ -f ${APP_PID_FILE} ]; then
                    PID=$(cat ${APP_PID_FILE})
                    kill $PID 2>/dev/null || true
                    rm -f ${APP_PID_FILE}
                    echo "Stopped Flask app (PID: $PID)"
                fi
            '''

            // Publish test results in Jenkins UI
            junit 'test-results.xml'

            echo '=== Pipeline finished ==='
        }

        success {
            echo '''
            ╔══════════════════════════════════╗
            ║  ✅  PIPELINE PASSED!            ║
            ║  All tests completed successfully ║
            ╚══════════════════════════════════╝
            '''
        }

        failure {
            echo '''
            ╔══════════════════════════════════╗
            ║  ❌  PIPELINE FAILED!            ║
            ║  Check the logs above for errors  ║
            ╚══════════════════════════════════╝
            '''
        }
    }
}
