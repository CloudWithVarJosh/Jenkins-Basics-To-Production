def call() {
    sh 'docker build --label maintainer=cloudwithvarjosh@gmail.com -t "$REPO:$TAG" .'
}