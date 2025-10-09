
# 1) Docker login (uses injected env vars)
echo "Logging in to Docker Hub..."
echo "$DOCKERHUB_PWD" | docker login -u "$DOCKERHUB_USER" --password-stdin

# 2) Image naming
IMAGE="docker.io/cloudwithvarjosh/cwvj-flask"
TAG="${BUILD_NUMBER}"

# 3) Build and push (exact tag + latest for convenience)
echo "Building image..."
docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" .

echo "Pushing image..."
docker push "$IMAGE:$TAG"
docker push "$IMAGE:latest"

# 4) Deploy on the Docker host (DooD)
echo "Deploying..."
docker pull "$IMAGE:$TAG"
docker rm -f cwvj-flask || true
docker run -d --name cwvj-flask -p 5000:5000 "$IMAGE:$TAG"

# 5) Quick smoke check (optional)
sleep 2
echo "Hit http://localhost:5000 to see the app."