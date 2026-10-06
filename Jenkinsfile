pipeline {
    // Runs on the Jenkins controller: it only checks out the repo and ships files.
    agent any

    environment {
        TARGET_HOST   = '65.0.27.119'     // <-- change
        TARGET_USER   = 'ec2-user'                  // <-- change (user on target server)
        SSH_CRED_ID   = 'ec2-target-key'         // <-- Jenkins "SSH Username with private key" credential ID
        DEPLOY_DIR    = '/home/ec2-user/python-app' // <-- folder on target server
        PORT          = '5000'
        SSH_OPTS      = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
    }

    stages {
        stage('Checkout (controller)') {
            steps {
                git branch: 'main', url: 'https://github.com/yashpal9370/python-app-deployment.git'
            }
        }

        stage('Copy app to target server') {
            steps {
                sshagent(credentials: [env.SSH_CRED_ID]) {
                    sh '''
                        set -e
                        echo "Preparing ${DEPLOY_DIR} on ${TARGET_HOST}..."
                        ssh ${SSH_OPTS} ${TARGET_USER}@${TARGET_HOST} "mkdir -p ${DEPLOY_DIR}"

                        echo "Copying the whole cloned repo to the target with scp..."
                        # '*' matches every non-hidden file/folder, so the whole app is copied
                        # and the hidden .git folder is left behind on the controller.
                        scp ${SSH_OPTS} -r * ${TARGET_USER}@${TARGET_HOST}:${DEPLOY_DIR}/
                    '''
                }
            }
        }

        stage('Install & Test (target server)') {
            steps {
                sshagent(credentials: [env.SSH_CRED_ID]) {
                    sh '''
                        ssh ${SSH_OPTS} ${TARGET_USER}@${TARGET_HOST} "bash -s" <<REMOTE
set -e
cd ${DEPLOY_DIR}

if ! command -v python3 >/dev/null 2>&1; then
    echo "Installing python3..."
    sudo yum install -y python3
fi

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

.venv/bin/python -m unittest discover -s tests
REMOTE
                    '''
                }
            }
        }

        stage('Deploy (target server)') {
            steps {
                sshagent(credentials: [env.SSH_CRED_ID]) {
                    sh '''
                        echo "Deploying on target server:"
                        ssh ${SSH_OPTS} ${TARGET_USER}@${TARGET_HOST} "hostname; hostname -I"

                        ssh ${SSH_OPTS} ${TARGET_USER}@${TARGET_HOST} "bash -s" <<REMOTE
cd ${DEPLOY_DIR}

echo "Stopping old process on port ${PORT}..."
fuser -k ${PORT}/tcp 2>/dev/null || true
sleep 2

echo "Starting application..."
PORT=${PORT} nohup .venv/bin/python app.py > app.log 2>&1 < /dev/null &
sleep 3
curl -sf http://127.0.0.1:${PORT}/ >/dev/null && echo "App is up on port ${PORT}" || (echo "App failed to start"; tail -n 30 app.log; exit 1)
REMOTE
                    '''
                }
            }
        }
    }

    post {
        success { echo "Deployed to http://${TARGET_HOST}:${PORT}/" }
        failure { echo 'Deployment failed - check the stage logs above.' }
    }
}