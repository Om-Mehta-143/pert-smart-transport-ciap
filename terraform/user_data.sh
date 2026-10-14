#!/bin/bash
# ==============================================================================
# Cloud-Init User Data Script for PERT Smart Transportation Web Application
# OS: Ubuntu 22.04 LTS (Jammy)
# Author: Om Vivek Mehta (TYCS_25 / 124BTCS1021)
# ==============================================================================

set -euo pipefail

# Output log redirection
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "=== Beginning Cloud-Init Automated Provisioning ==="

# 1. System Package Update
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y

# 2. Install Docker Community Edition
apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io

# 3. Enable and Start Docker Service
systemctl enable docker
systemctl start docker

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# 4. Pull and Run Production Container
DOCKER_IMAGE="${docker_image}"
echo "Pulling Docker image: $DOCKER_IMAGE"
docker pull "$DOCKER_IMAGE"

# Run container mapping port 80 (external HTTP) to port 5000 (Flask internal)
# Also map port 5000 to port 5000 for direct port testing
echo "Launching hardened container..."
docker run -d \
  --name pert-app-prod \
  --restart always \
  -p 80:5000 \
  -p 5000:5000 \
  "$DOCKER_IMAGE"

# 5. Local verification probe
sleep 10
curl -f http://localhost:5000/healthz && echo "Application successfully initialized."

echo "=== Cloud-Init Provisioning Completed Successfully ==="
