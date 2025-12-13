def call() {
                sh 'docker rm -f $REPO || true'
                sh 'docker run -d --name $REPO --restart unless-stopped -p "$PORT:$PORT" "$REPO:$TAG"'
}